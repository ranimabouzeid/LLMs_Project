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
    A student's explanation was missing key sub-concepts. Identify the underlying 
    PREREQUISITE concepts (Foundations) they likely don't understand.

    REQUIRED JSON FORMAT:
    [
      {
        "topic": "The main topic being discussed",
        "prerequisite_concept": "The foundational concept missing",
        "severity": 3,
        "evidence": "Why you think this is missing"
      }
    ]
    
    CRITICAL: You must provide ALL 4 fields for every entry.
    """
    
    user_msg = f"Question: {query}\nMissing Concepts: {', '.join(missing_ideas)}"
    
    try:
        res = llm_client.chat(system_prompt, user_msg, json_mode=True)
        
        # Handle different potential JSON structures
        if isinstance(res, dict):
            data = res.get("debts", []) or res.get("prerequisites", []) or [res]
        else:
            data = res
            
        debts = []
        for item in data:
            if not isinstance(item, dict): continue
            
            # DEFAULT GUARD: Fill in any missing keys to prevent Pydantic crashes
            topic = item.get("topic") or query[:50]
            prereq = item.get("prerequisite_concept") or item.get("prerequisite") or "General ML Foundation"
            sev = item.get("severity") or 3
            evid = item.get("evidence") or f"Inferred from lack of coverage on {', '.join(missing_ideas[:2])}"
            
            debts.append(DebtEntry(
                topic=str(topic),
                prerequisite_concept=str(prereq),
                severity=int(sev),
                evidence=str(evid)
            ))
        return debts
    except Exception as e:
        print(f"⚠️ Debt Detection failed: {e}")
        return []
