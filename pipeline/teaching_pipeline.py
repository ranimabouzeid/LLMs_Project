import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from agents.decomposer import Decomposer
from agents.retrieval_judge import RetrievalJudge
from agents.explanation_agent import ExplanationAgent
from agents.quality_agent import QualityAgent # Consolidated Auditor
from tools.embedder import ChromaEmbedder
from memory.memory_manager import MemoryManager
from memory.concept_debt_ledger import ConceptDebtLedger
from memory.preference_memory import get_preferences
from agents.debt_detector import filter_relevant_debts
from pipeline.schemas import Chunk, KeyIdea, DebtEntry

class AblationConfig(BaseModel):
    """Toggles for the Ablation Study."""
    use_tarj: bool = True
    use_ecv: bool = True
    use_cdl: bool = True
    use_domain_adaptation: bool = True

class TeachingPipeline:
    """
    The Orchestrator. Consolidates steps to reduce API quota consumption.
    """
    def __init__(self):
        self.decomposer = Decomposer()
        self.judge = RetrievalJudge(threshold=5.0)
        self.explainer = ExplanationAgent()
        self.quality_agent = QualityAgent() # Replaces ECV and QuestionGen
        self.knowledge_store = ChromaEmbedder()
        self.memory = MemoryManager()
        self.cdl = ConceptDebtLedger()

    async def run_pipeline(self, 
                           query: str, 
                           student_id: str = "default_student", 
                           history: List[Dict[str, str]] = [],
                           config: Optional[AblationConfig] = None) -> Dict[str, Any]:
        """
        Executes the flow asynchronously with request consolidation.
        """
        if config is None:
            config = AblationConfig()

        print(f"\n🚀 [Pipeline] Processing: '{query}' (Quota Optimized)")

        # STEP 1: Context
        open_debts = []
        preferences = {}
        if config.use_cdl:
            all_open_debts = self.cdl.get_active_debts(student_id, query)
            open_debts = filter_relevant_debts(query, all_open_debts)
            prefs_raw = get_preferences(student_id)
            preferences = {p[0]: p[1] for p in prefs_raw}

        # STEP 2: Retrieval
        search_results = self.knowledge_store.search(query, k=8, filter={"student_id": student_id})
        raw_chunks = [
            Chunk(text=doc.page_content, metadata=doc.metadata, 
                  source_file=doc.metadata.get("source_file"), page_number=doc.metadata.get("page"))
            for doc in search_results
        ]

        # STEP 3 & 4: Parallel Judging and Decomposition
        async def get_judged_chunks():
            return self.judge.score_chunks(query, raw_chunks) if config.use_tarj else raw_chunks

        async def get_key_ideas():
            return self.decomposer.decompose(query)

        approved_chunks, key_ideas = await asyncio.gather(get_judged_chunks(), get_key_ideas())

        # STEP 5: Explanation
        explanation = self.explainer.generate_explanation(
            query=query, key_ideas=key_ideas, approved_chunks=approved_chunks,
            open_debts=open_debts, history=history, preferences=preferences,
            use_domain_adaptation=config.use_domain_adaptation
        )

        # Mark explained debts as repaired
        if config.use_cdl and open_debts:
            for debt in open_debts:
                self.cdl.mark_as_repaired(student_id, debt.prerequisite_concept)

        # STEP 6 & 7: Consolidated Audit and Question Generation (Saves 1 API Call)
        report, questions = None, []
        if config.use_ecv:
            report, questions = self.quality_agent.perform_final_audit(query, explanation, key_ideas)
        else:
            # Fallback if ECV is ablated: generate questions only (Still needs an API call)
            # To be truly ablated, we just return empty
            pass

        # STEP 8: Update Memory
        self.memory.process_interaction(
            student_id=student_id,
            query=query,
            explanation=explanation,
            key_ideas=key_ideas,
            missing_ideas=report.missing_ideas if report else []
        )

        return {
            "query": query,
            "explanation": explanation,
            "key_ideas": key_ideas,
            "sources": approved_chunks,
            "coverage": report,
            "questions": questions
        }

# Global instance
pipeline = TeachingPipeline()
