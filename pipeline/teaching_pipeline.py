import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from agents.decomposer import Decomposer
from agents.retrieval_judge import RetrievalJudge
from agents.explanation_agent import ExplanationAgent
from agents.coverage_verifier import verify_coverage
from agents.question_generator import generate_question_set
from tools.embedder import ChromaEmbedder
from memory.memory_manager import MemoryManager
from memory.concept_debt_ledger import ConceptDebtLedger
from pipeline.schemas import Chunk, KeyIdea, DebtEntry

class AblationConfig(BaseModel):
    """Toggles for the Ablation Study."""
    use_tarj: bool = True
    use_ecv: bool = True
    use_cdl: bool = True
    use_domain_adaptation: bool = True

class TeachingPipeline:
    """
    The Orchestrator. Tied together with Asyncio for high performance.
    """
    def __init__(self):
        self.decomposer = Decomposer()
        self.judge = RetrievalJudge(threshold=5.0)
        self.explainer = ExplanationAgent()
        self.knowledge_store = ChromaEmbedder()
        self.memory = MemoryManager()
        self.cdl = ConceptDebtLedger()

    async def run_pipeline(self, 
                           query: str, 
                           student_id: str = "default_student", 
                           history: List[Dict[str, str]] = [],
                           config: Optional[AblationConfig] = None) -> Dict[str, Any]:
        """
        Executes the full pedagogical flow asynchronously.
        """
        if config is None:
            config = AblationConfig()

        print(f"\n🚀 [Pipeline] Processing: '{query}' (Ablation: {config.dict()})")

        # STEP 1: Debt Check
        open_debts = []
        if config.use_cdl:
            open_debts = self.cdl.get_active_debts(student_id, query)

        # STEP 2: Retrieval
        search_results = self.knowledge_store.search(query, k=8, filter={"student_id": student_id})
        raw_chunks = [
            Chunk(text=doc.page_content, metadata=doc.metadata, 
                  source_file=doc.metadata.get("source_file"), page_number=doc.metadata.get("page"))
            for doc in search_results
        ]

        # --- PARALLEL BLOCK (Steps 3 & 4) ---
        # We wrap these in threads since they are currently blocking LLM calls
        loop = asyncio.get_event_loop()
        
        async def get_judged_chunks():
            if config.use_tarj:
                return self.judge.score_chunks(query, raw_chunks)
            return raw_chunks # Skip filtering

        async def get_key_ideas():
            return self.decomposer.decompose(query)

        # Run both at the same time
        approved_chunks, key_ideas = await asyncio.gather(
            get_judged_chunks(),
            get_key_ideas()
        )

        # STEP 5: Generate Explanation
        explanation = self.explainer.generate_explanation(
            query=query,
            key_ideas=key_ideas,
            approved_chunks=approved_chunks,
            open_debts=open_debts,
            history=history,
            use_domain_adaptation=config.use_domain_adaptation # Added flag
        )

        # STEP 6: ECV Coverage Check
        report = None
        if config.use_ecv:
            report = verify_coverage(key_ideas, explanation)

        # STEP 7: Question Generation
        question_data = generate_question_set(query, [idea.name for idea in key_ideas])
        questions = question_data.get("mcqs", []) + question_data.get("short_answer", [])

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
