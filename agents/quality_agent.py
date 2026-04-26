import json
from typing import List, Dict, Any, Tuple
from pipeline.schemas import CoverageReport, KeyIdea
from tools.llm_client import llm_client

class QualityAgent:
    """
    Consolidates Coverage Verification (ECV) and Question Generation
    into a single API call to save quota and reduce latency.
    """
    
    def perform_final_audit(self, query: str, explanation: str, key_ideas: List[KeyIdea]) -> Tuple[CoverageReport, List[Dict[str, Any]]]:
        """
        Audits the explanation for coverage AND generates assessment questions.
        Returns (CoverageReport, List of Questions)
        """
        print("🔍 [QualityAgent] Performing semantic audit and generating questions...")

        if not key_ideas:
            return (
                CoverageReport(is_complete=True, score=1.0, covered_ideas=[], missing_ideas=[], feedback="No ideas."),
                []
            )

        system_prompt = """
        You are an educational auditor and assessment designer.
        Your task is two-fold:
        1. AUDIT: Compare the 'Key Ideas' against the 'Explanation' to see what was covered.
        2. ASSESSMENT: Generate 3 MCQs and 2 Short Answer questions based on the topic.

        For MCQs, ensure 4 options (A, B, C, D) and an explanation.

        Return EXACT JSON:
        {
          "audit": {
            "covered_ideas": ["..."],
            "missing_ideas": ["..."],
            "feedback": "..."
          },
          "questions": {
            "mcqs": [
                {"question": "...", "options": {"A": "...", "B": "...", "C": "...", "D": "..."}, "correct_answer": "...", "explanation": "..."}
            ],
            "short_answer": ["Question 1", "Question 2"]
          }
        }
        """

        ideas_list = "\n".join([f"- {i.name}: {i.description}" for i in key_ideas])
        user_message = f"TOPIC: {query}\n\nEXPLANATION:\n{explanation}\n\nKEY IDEAS:\n{ideas_list}"

        try:
            res = llm_client.chat(system_prompt, user_message, json_mode=True)
            
            # 1. Parse Audit
            audit_data = res.get("audit", {})
            covered = audit_data.get("covered_ideas", [])
            missing = audit_data.get("missing_ideas", [])
            score = len(covered) / len(key_ideas) if key_ideas else 1.0
            
            report = CoverageReport(
                is_complete=(score >= 0.7),
                score=score,
                covered_ideas=covered,
                missing_ideas=missing,
                feedback=audit_data.get("feedback", "Audit complete.")
            )

            # 2. Parse Questions
            q_data = res.get("questions", {})
            questions = q_data.get("mcqs", []) + q_data.get("short_answer", [])

            return report, questions

        except Exception as e:
            print(f"⚠️ Quality Audit failed: {e}")
            return (
                CoverageReport(is_complete=True, score=0.0, covered_ideas=[], missing_ideas=[], feedback="Audit error."),
                []
            )
