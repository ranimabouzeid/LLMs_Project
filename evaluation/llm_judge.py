import json
from tools.llm_client import llm_client

def evaluate_response(query: str, explanation: str) -> float:
    """Uses LLM-as-a-judge to score the pedagogical quality of the response."""
    system_prompt = """
    You are an expert evaluator of educational content.
    Score the provided explanation on a scale of 1 to 10 for conceptual depth, clarity, and pedagogical value.
    Return exact JSON: {"score": 8.5, "reasoning": "..."}
    """
    user_msg = f"Question: {query}\n\nExplanation: {explanation}"
    try:
        res = llm_client.chat(system_prompt, user_msg, json_mode=True)
        return float(res.get("score", 0.0))
    except Exception:
        return 0.0
