import json
from typing import List
from tools.llm_client import llm_client
from pipeline.schemas import DebtEntry

def detect_concept_debt(query: str, missing_ideas: List[str]) -> List[DebtEntry]:
    """
    Analyzes why ideas were missing and infers prerequisite gaps.
    """
    system_prompt = """
    You are a pedagogical analyzer for an ML/DL/LLM course.
    Identify the underlying PREREQUISITE concepts they likely don't understand.

    REQUIRED JSON FORMAT:
    [
      {
        "topic": "The main topic",
        "prerequisite_concept": "The missing foundation",
        "severity": 3,
        "evidence": "Why you think this is missing"
      }
    ]
    """
    user_msg = f"Question: {query}\nMissing Concepts: {', '.join(missing_ideas)}"
    try:
        res = llm_client.chat(system_prompt, user_msg, json_mode=True)
        data = res if isinstance(res, list) else [res]
        debts = []
        for item in data:
            debts.append(DebtEntry(
                topic=item.get("topic", query[:50]),
                prerequisite_concept=item.get("prerequisite_concept", "General Foundation"),
                severity=item.get("severity", 3),
                evidence=item.get("evidence", "Inferred gap.")
            ))
        return debts
    except Exception:
        return []

def filter_relevant_debts(query: str, all_debts: List[DebtEntry]) -> List[DebtEntry]:
    """
    Filters and prioritizes the top 3 debts related to the current query.
    """
    if not all_debts:
        return []

    system_prompt = """
    You are a pedagogical coordinator. Given a student's current question and a list of their 
    previous "Knowledge Debts" (unlearned prerequisites), identify which debts are 
    MOST RELEVANT to help them understand the current question.

    Return a JSON list of the INDICES of the top 3 most relevant debts.
    Example: [0, 2, 5]
    If none are relevant, return [].
    """
    
    debt_descriptions = [f"{i}: {d.prerequisite_concept} (Related to {d.topic})" for i, d in enumerate(all_debts)]
    user_msg = f"Current Question: {query}\n\nAll Open Debts:\n" + "\n".join(debt_descriptions)
    
    try:
        indices = llm_client.chat(system_prompt, user_msg, json_mode=True)
        if isinstance(indices, dict): indices = indices.get("indices", [])
        
        filtered = [all_debts[i] for i in indices if i < len(all_debts)]
        return filtered[:3] # Ensure max 3
    except Exception:
        # Fallback: Just return top 3 by severity if AI filter fails
        return sorted(all_debts, key=lambda x: x.severity, reverse=True)[:3]
