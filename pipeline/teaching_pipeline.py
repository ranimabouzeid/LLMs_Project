from typing import Dict, Any, List
from agents.decomposer import Decomposer
from agents.retrieval_judge import RetrievalJudge
from agents.explanation_agent import ExplanationAgent
from pipeline.schemas import Chunk, KeyIdea, DebtEntry

class TeachingPipeline:
    """
    The Orchestrator. Ties all 8 steps of the TutorMind process together.
    """
    def __init__(self):
        self.decomposer = Decomposer()
        self.judge = RetrievalJudge(threshold=5.0)
        self.explainer = ExplanationAgent()

    def run_pipeline(self, query: str) -> Dict[str, Any]:
        """
        Executes the full pedagogical flow.
        """
        print(f"\n🚀 Starting Teaching Pipeline for: '{query}'")

        # STEP 1: Debt Check (Placeholder for Member 3)
        # In the future: open_debts = memory_manager.get_active_debts(query)
        open_debts = [] 

        # STEP 2: Retrieval (Placeholder for Member 2)
        # In the future: raw_chunks = knowledge_store.search(query)
        print("📡 Step 2: Retrieving course materials (Mocked)...")
        raw_chunks = [
            Chunk(text="Self-attention allows the model to focus on relevant words.", metadata={"source": "Course_Slides.pdf"}),
            Chunk(text="x = y + z", metadata={"source": "code.py"})
        ]

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
            open_debts=open_debts
        )

        # STEP 6: ECV Coverage Check (Placeholder for Member 2)
        # In the future: coverage = coverage_verifier.verify(explanation, key_ideas)
        coverage_report = "Coverage check will appear here once Member 2 completes ECV."

        # STEP 7: Question Generation (Placeholder for Member 2/3)
        # In the future: questions = question_generator.generate(key_ideas)
        questions = []

        return {
            "query": query,
            "explanation": explanation,
            "key_ideas": key_ideas,
            "sources": approved_chunks,
            "coverage": coverage_report,
            "questions": questions
        }

# Global instance
pipeline = TeachingPipeline()
