import asyncio
import threading
import time
from typing import Dict, Any, List, Optional, Generator
from pydantic import BaseModel

from agents.decomposer import Decomposer
from agents.retrieval_judge import RetrievalJudge
from agents.explanation_agent import ExplanationAgent
from agents.quality_agent import QualityAgent
from tools.embedder import ChromaEmbedder
from memory.memory_manager import MemoryManager
from memory.concept_debt_ledger import ConceptDebtLedger
from memory.preference_memory import get_preferences
from memory.knowledge_store import KnowledgeCache
from agents.debt_detector import filter_relevant_debts
from pipeline.schemas import Chunk, KeyIdea, DebtEntry
from tools.llm_client import llm_client

class AblationConfig(BaseModel):
    use_tarj: bool = True
    use_ecv: bool = True
    use_cdl: bool = True
    use_domain_adaptation: bool = True
    use_cache: bool = True # Added cache toggle

class TeachingPipeline:
    def __init__(self):
        self.decomposer = Decomposer()
        self.judge = RetrievalJudge(threshold=5.0)
        self.explainer = ExplanationAgent()
        self.quality_agent = QualityAgent()
        self.knowledge_store = ChromaEmbedder()
        self.memory = MemoryManager()
        self.cdl = ConceptDebtLedger()
        self.cache = KnowledgeCache()

    def generate_explanation_stream(self, 
                                    query: str, 
                                    key_ideas: List[KeyIdea], 
                                    approved_chunks: List[Chunk], 
                                    open_debts: List[DebtEntry], 
                                    history: List[Dict], 
                                    preferences: Dict,
                                    use_domain_adaptation: bool) -> Generator[str, None, None]:
        context_text = "\n\n".join([f"[Source: {c.source_file or 'Unknown'}] {c.text}" for c in approved_chunks])
        ideas_text = "\n".join([f"- {i.name}: {i.description}" for i in key_ideas])
        
        pref_text = ""
        if preferences:
            pref_text = "STUDENT PREFERENCES:\n" + "\n".join([f"- {k}: {v}" for k, v in preferences.items()])
        
        repair_instruction = ""
        if open_debts:
            repair_instruction = "\n### 🛠️ PREREQUISITE REPAIR NEEDED\nBriefly explain: " + ", ".join([d.prerequisite_concept for d in open_debts])
            
        system_prompt = self.explainer.domain_prompt if (use_domain_adaptation and self.explainer.domain_prompt) else self.explainer.default_prompt
        user_msg = f"{pref_text}\n{repair_instruction}\nSTUDENT QUESTION: {query}\n\nIDEAS: {ideas_text}\n\nSOURCES: {context_text}"
        
        return llm_client.stream_chat(system_prompt, user_msg)

    async def run_pipeline(self, 
                           query: str, 
                           student_id: str = "default_student", 
                           history: List[Dict[str, str]] = [],
                           config: Optional[AblationConfig] = None) -> Dict[str, Any]:
        if config is None: config = AblationConfig()

        # 1. Context
        all_open_debts = self.cdl.get_active_debts(student_id, query)
        open_debts = filter_relevant_debts(query, all_open_debts)
        prefs_raw = get_preferences(student_id)
        preferences = {p[0]: p[1] for p in prefs_raw}

        # 2. CACHE CHECK (Respect the toggle)
        cached_result = self.cache.get(query) if config.use_cache else None
        
        if cached_result:
            key_ideas, approved_chunks = cached_result
        else:
            search_results = self.knowledge_store.search(query, k=8, filter={"student_id": student_id})
            # FIX: Restore metadata mapping to avoid "Unknown Source"
            raw_chunks = [
                Chunk(
                    text=doc.page_content, 
                    metadata=doc.metadata,
                    source_file=doc.metadata.get("source_file") or doc.metadata.get("filename"),
                    page_number=doc.metadata.get("page")
                ) for doc in search_results
            ]

            async def get_judged_chunks(): return self.judge.score_chunks(query, raw_chunks) if config.use_tarj else raw_chunks
            async def get_key_ideas(): return self.decomposer.decompose(query)
            
            approved_chunks, key_ideas = await asyncio.gather(get_judged_chunks(), get_key_ideas())
            self.cache.set(query, key_ideas, approved_chunks)

        # 3. Generating Explanation (Main task)
        explanation = self.explainer.generate_explanation(
            query=query, key_ideas=key_ideas, approved_chunks=approved_chunks,
            open_debts=open_debts, history=history, preferences=preferences,
            use_domain_adaptation=config.use_domain_adaptation
        )

        # 4. Background: Quality Audit & Memory (Saves API calls in the main thread)
        def bg_audit():
            # Add a tiny delay to avoid 429 collision with the main response
            time.sleep(2)
            report, questions = self.quality_agent.perform_final_audit(query, explanation, key_ideas)
            self.memory.process_interaction(student_id, query, explanation, key_ideas, report.missing_ideas if report else [])
            for d in open_debts: self.cdl.mark_as_repaired(student_id, d.prerequisite_concept)

        threading.Thread(target=bg_audit, daemon=True).start()

        # To keep UI logic simple, we generate generic fallback questions if the background is slow
        # but the main UI will use the QualityAgent's questions in the next interaction.
        return {
            "query": query, "explanation": explanation, "key_ideas": key_ideas,
            "sources": approved_chunks, "coverage": None, "questions": [] # UI will re-run audit for visual feedback
        }

pipeline = TeachingPipeline()
