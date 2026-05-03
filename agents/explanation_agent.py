import os
from typing import List, Optional, Dict
from tools.llm_client import llm_client
from pipeline.prompts import EXPLANATION_SYSTEM_PROMPT
from pipeline.schemas import KeyIdea, Chunk, DebtEntry
from pathlib import Path

class ExplanationAgent:
    """
    The main agent responsible for generating the structured pedagogical response.
    """
    def __init__(self):
        self.default_prompt = EXPLANATION_SYSTEM_PROMPT
        self.domain_prompt = ""
        
        # Load path from ENV or default
        env_path = os.getenv("DOMAIN_PROMPT_PATH", "pipeline/domain_prompt.txt")
        prompt_path = Path(env_path)
        
        if prompt_path.exists():
            self.domain_prompt = prompt_path.read_text(encoding="utf-8")

    def generate_explanation(self, 
                             query: str, 
                             key_ideas: List[KeyIdea], 
                             approved_chunks: List[Chunk], 
                             open_debts: List[DebtEntry] = [],
                             history: List[Dict[str, str]] = [],
                             preferences: Dict[str, str] = {},
                             use_domain_adaptation: bool = True) -> str:
        """
        Generates a deep explanation. Respects student preferences and repairs debts.
        """
        # Select prompt based on configuration
        system_prompt = self.domain_prompt if (use_domain_adaptation and self.domain_prompt) else self.default_prompt
        
        # 1. Build the context from retrieved chunks
        context_text = "\n\n".join([f"[Source: {c.metadata.get('source_file', 'Unknown')}] {c.text}" for c in approved_chunks])
        
        # 2. Build the list of must-cover ideas
        ideas_text = "\n".join([f"- {i.name}: {i.description}" for i in key_ideas])
        
        # 3. Format History
        history_text = ""
        if history:
            history_text = "CONVERSATION HISTORY:\n"
            for msg in history[-5:]:
                role = "Student" if msg["role"] == "user" else "TutorMind"
                history_text += f"{role}: {msg['content'][:500]}...\n"
            history_text += "\n"

        # 4. Handle Preferences
        pref_text = ""
        if preferences:
            pref_text = "STUDENT PREFERENCES:\n"
            for k, v in preferences.items():
                pref_text += f"- {k.replace('_', ' ').title()}: {v}\n"
            pref_text += "\n"

        # 5. Handle Prerequisite Repairs (Modified to ask for explanation)
        repair_instruction = ""
        if open_debts:
            repair_instruction = "\n### 🛠️ PREREQUISITE REPAIR NEEDED\n"
            repair_instruction += "The student is missing the following prerequisites. You MUST explain them briefly and intuitively BEFORE answering their main question:\n"
            for debt in open_debts:
                repair_instruction += f"- {debt.prerequisite_concept}: (Why they missed it: {debt.evidence})\n"
            repair_instruction += "\n"

        # 6. Construct final prompt
        full_user_msg = f"""
{history_text}
{pref_text}
{repair_instruction}
STUDENT QUESTION/RESPONSE: {query}

ESSENTIAL KEY IDEAS TO COVER:
{ideas_text}

SOURCE MATERIAL (Use ONLY these facts):
{context_text}

INSTRUCTIONS:
- If there are prerequisites listed above, explain them intuitively first in a 'Prerequisite Foundations' section.
- Follow the student's preferences if provided.
- If the student is answering a question you asked, evaluate their answer first.
- If they are asking a new question, follow the 'DeepStudy Coach' structure: Analogy, Connection, Breakdown, The Trap, and Challenge.
"""
        
        explanation = llm_client.chat(
            system_prompt=system_prompt,
            user_message=full_user_msg,
            json_mode=False 
        )

        return explanation
