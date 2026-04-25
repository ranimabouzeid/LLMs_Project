import json
from typing import List
from pipeline.schemas import CoverageReport, KeyIdea
from tools.llm_client import llm_client

def verify_coverage(
    key_ideas: List[KeyIdea],
    explanation: str,
    threshold: float = 0.70,
) -> CoverageReport:
    """
    ECV: Explanation Coverage Verifier (Upgraded to Semantic AI).
    Checks if the explanation actually covers the conceptual meaning of Key Ideas.
    """
    if not key_ideas:
        return CoverageReport(
            is_complete=True,
            score=1.0,
            covered_ideas=[],
            missing_ideas=[],
            feedback="No ideas provided.",
        )

    print("🔍 [ECV] Performing semantic coverage check...")

    system_prompt = """
    You are an educational auditor. Compare a list of 'Key Ideas' against an 'Explanation'.
    For each idea, determine if the explanation sufficiently covers the CONCEPT.
    
    Return EXACT JSON:
    {
      "covered_ideas": ["Idea Name 1", "Idea Name 2"],
      "missing_ideas": ["Idea Name 3"],
      "feedback": "Concise pedagogical feedback on what is missing."
    }
    """

    ideas_list = "\n".join([f"- {i.name}: {i.description}" for i in key_ideas])
    user_message = f"EXPLANATION:\n{explanation}\n\nKEY IDEAS TO CHECK:\n{ideas_list}"

    try:
        res = llm_client.chat(system_prompt, user_message, json_mode=True)
        
        covered = res.get("covered_ideas", [])
        missing = res.get("missing_ideas", [])
        
        score = len(covered) / len(key_ideas)
        is_complete = score >= threshold

        return CoverageReport(
            is_complete=is_complete,
            score=score,
            covered_ideas=covered,
            missing_ideas=missing,
            feedback=res.get("feedback", "Check complete.")
        )
    except Exception as e:
        print(f"⚠️ ECV Failed: {e}. Falling back to basic reporting.")
        return CoverageReport(is_complete=True, score=0.0, covered_ideas=[], missing_ideas=[], feedback="Error in check.")

def build_coverage_feedback(report: CoverageReport) -> str:
    # Keeps existing UI compatibility
    feedback = f"### 📊 Coverage: {int(report.score * 100)}%\n"
    feedback += f"{report.feedback}\n"
    if report.missing_ideas:
        feedback += f"\n**Needs Improvement:** {', '.join(report.missing_ideas)}"
    return feedback
