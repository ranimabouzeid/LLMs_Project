from typing import List, Dict, Any


def generate_short_answer_questions(missing_ideas: List[str]) -> List[str]:
    """
    Generates simple concept-checking questions from missing ideas.
    """

    questions = []

    for idea in missing_ideas:
        questions.append(f"Explain this concept in your own words: {idea}")

    return questions


def generate_mcqs_from_missing_ideas(missing_ideas: List[str]) -> List[Dict[str, Any]]:
    """
    Generates basic MCQs from missing ideas.
    These can later be improved using Gemini.
    """

    mcqs = []

    for index, idea in enumerate(missing_ideas, start=1):
        mcqs.append(
            {
                "question": f"Which statement best describes: {idea}?",
                "options": {
                    "A": f"{idea}",
                    "B": "An unrelated concept from the lecture",
                    "C": "A random memorized definition without explanation",
                    "D": "A concept that is not connected to the current topic",
                },
                "answer": "A",
                "explanation": f"Option A is correct because it directly represents the missing idea: {idea}.",
            }
        )

    return mcqs


def generate_repair_questions(topic: str, missing_ideas: List[str]) -> List[str]:
    """
    Generates follow-up repair questions to help the student fix weak areas.
    """

    questions = []

    for idea in missing_ideas:
        questions.append(
            f"For the topic '{topic}', why is this idea important: {idea}?"
        )

    return questions


def generate_question_set(topic: str, missing_ideas: List[str]) -> Dict[str, Any]:
    """
    Returns a complete question set.
    """

    return {
        "topic": topic,
        "short_answer": generate_short_answer_questions(missing_ideas),
        "mcqs": generate_mcqs_from_missing_ideas(missing_ideas),
        "repair_questions": generate_repair_questions(topic, missing_ideas),
    }