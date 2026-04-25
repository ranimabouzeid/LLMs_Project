from typing import List, Dict, Any
from tools.llm_client import llm_client

def generate_question_set(topic: str, missing_ideas: List[str]) -> Dict[str, Any]:
    """
    Uses Gemini to generate deep-thinking questions for the student.
    """
    if not missing_ideas:
        return {"mcqs": [], "short_answer": []}

    system_prompt = """
    You are a pedagogical assessment expert. Your goal is to generate 
    challenging, deep-thinking questions that test understanding, not memorization.
    
    Return your response in EXACT JSON format:
    {
      "mcqs": [
        {"question": "...", "options": {"A": "...", "B": "..."}, "answer": "A", "explanation": "..."}
      ],
      "short_answer": ["Question 1", "Question 2"]
    }
    """
    
    user_message = f"Topic: {topic}\nMissing Concepts: {', '.join(missing_ideas)}"
    
    response = llm_client.chat(system_prompt, user_message, json_mode=True)
    return response

def generate_repair_questions(topic: str, missing_ideas: List[str]) -> List[str]:
    # Legacy wrapper for compatibility
    res = generate_question_set(topic, missing_ideas)
    return res.get("short_answer", [])
