import json
from typing import List, Dict, Any
from tools.llm_client import llm_client

def generate_question_set(topic: str, key_ideas: List[str]) -> Dict[str, Any]:
    """
    Generates a set of MCQs and Short Answer questions for the student.
    """
    system_prompt = """
    You are a pedagogical assessment designer. Based on the topic and key ideas, 
    generate 3 MCQs and 2 Short Answer questions.
    
    For MCQs, ensure:
    - 4 options (A, B, C, D)
    - One clear correct answer
    - A 'pedagogical explanation' for WHY that answer is correct.

    Return EXACT JSON:
    {
      "mcqs": [
        {"question": "...", "options": {"A": "...", "B": "...", "C": "...", "D": "..."}, "correct_answer": "A", "explanation": "..."}
      ],
      "short_answer": ["Question 1", "Question 2"]
    }
    """
    user_msg = f"Topic: {topic}\nKey Ideas: {', '.join(key_ideas)}"
    try:
        return llm_client.chat(system_prompt, user_msg, json_mode=True)
    except Exception:
        return {"mcqs": [], "short_answer": []}

def evaluate_short_answer(question: str, student_answer: str) -> str:
    """
    Direct, fast evaluation of a short answer using only an LLM call.
    """
    system_prompt = "You are a helpful tutor. Briefly evaluate the student's answer to the given question. State if they are correct, partially correct, or incorrect, and provide the 'Ideal' concept they should have mentioned."
    user_msg = f"Question: {question}\nStudent Answer: {student_answer}"
    
    try:
        # Fast direct call
        return llm_client.chat(system_prompt, user_msg, json_mode=False)
    except Exception as e:
        return f"Could not evaluate at this time: {e}"
