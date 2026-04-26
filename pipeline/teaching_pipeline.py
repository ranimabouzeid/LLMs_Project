from typing import Dict, Any, List
from agents.decomposer import Decomposer
from agents.retrieval_judge import RetrievalJudge
from agents.explanation_agent import ExplanationAgent
from agents.coverage_verifier import verify_coverage, build_coverage_feedback
from agents.question_generator import generate_question_set
from tools.embedder import ChromaEmbedder
from memory.memory_manager import MemoryManager
from memory.concept_debt_ledger import ConceptDebtLedger
from pipeline.schemas import Chunk, KeyIdea, DebtEntry

class TeachingPipeline:
    """
    The Orchestrator. Ties all 8 steps of the TutorMind process together.
    """
    def __init__(self):
        self.decomposer = Decomposer()
        self.judge = RetrievalJudge(threshold=5.0)
        self.explainer = ExplanationAgent()
        self.knowledge_store = ChromaEmbedder()
        self.memory = MemoryManager()
        self.cdl = ConceptDebtLedger()

    def run_pipeline(self, 
                     query: str, 
                     student_id: str = "default_student", 
                     history: List[Dict[str, str]] = []) -> Dict[str, Any]:
        """
        Executes the full pedagogical flow.
        """
        print(f"\n🚀 Starting Teaching Pipeline for: '{query}'")

        # STEP 1: Debt Check
        print("🔍 Step 1: Checking for previous concept debts...")
        open_debts = self.cdl.get_active_debts(student_id, query)
        if open_debts:
            print(f"   ⚠️ Found {len(open_debts)} prerequisites that need repair.")

        # STEP 2: Real Retrieval with student_id filtering
        print(f"📡 Step 2: Retrieving course materials for {student_id}...")
        search_results = self.knowledge_store.search(
            query, 
            k=5, 
            filter={"student_id": student_id} 
        )
        
        # Convert LangChain Documents back to our Chunk schema
        raw_chunks = []
        for doc in search_results:
            raw_chunks.append(Chunk(
                text=doc.page_content,
                metadata=doc.metadata,
                source_file=doc.metadata.get("source_file"),
                page_number=doc.metadata.get("page")
            ))

        # STEP 3: TARJ (Your Quality Filter)
        print("⚖️ Step 3: Judging pedagogical quality...")
        approved_chunks = self.judge.score_chunks(query, raw_chunks)

        # STEP 4: Decompose (Your Syllabus Brain)
        print("🧠 Step 4: Decomposing topic into Key Ideas...")
        key_ideas = self.decomposer.decompose(query)

        # STEP 5: Generate Explanation (Your Intuition Generator)
        print("📝 Step 5: Generating deep explanation...")
        explanation = self.explainer.generate_explanation(
            query=query,
            key_ideas=key_ideas,
            approved_chunks=approved_chunks,
            open_debts=open_debts,
            history=history
        )

        # STEP 6: ECV Coverage Check
        print("🔍 Step 6: Verifying explanation coverage...")
        report = verify_coverage(key_ideas, explanation)

        # STEP 7: Question Generation
        print("❓ Step 7: Generating assessment questions...")
        missing_ideas = report.missing_ideas if 'report' in locals() else []
        question_data = generate_question_set(query, [idea.name for idea in key_ideas])
        questions = question_data.get("mcqs", []) + question_data.get("short_answer", [])

        # STEP 8: Update Memory
        self.memory.process_interaction(
            student_id=student_id,
            query=query,
            explanation=explanation,
            key_ideas=key_ideas,
            missing_ideas=missing_ideas
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
