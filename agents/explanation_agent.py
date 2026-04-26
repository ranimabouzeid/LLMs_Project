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
        
        prompt_path = Path("pipeline/domain_prompt.txt")
        if prompt_path.exists():
            self.domain_prompt = prompt_path.read_text(encoding="utf-8")

    def generate_explanation(self, 
                             query: str, 
                             key_ideas: List[KeyIdea], 
                             approved_chunks: List[Chunk], 
                             open_debts: List[DebtEntry] = [],
                             history: List[Dict[str, str]] = [],
                             use_domain_adaptation: bool = True) -> str:
        """
        Generates a deep explanation. Can toggle domain adaptation for ablation studies.
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

        # 4. Handle Prerequisite Repairs
        repair_text = ""
        if open_debts:
            repair_text = "### 🛠️ Prerequisite Foundations\n"
            repair_text += "Before we dive in, let's quickly clarify some concepts you struggled with recently:\n"
            for debt in open_debts:
                repair_text += f"- {debt.prerequisite_concept}: {debt.evidence}\n"
            repair_text += "\n---\n\n"

        # 5. Construct final prompt
        full_user_msg = f"""
{history_text}
STUDENT QUESTION/RESPONSE: {query}

ESSENTIAL KEY IDEAS TO COVER:
{ideas_text}

SOURCE MATERIAL (Use ONLY these facts):
{context_text}

INSTRUCTIONS:
- If the student is answering a question you asked, evaluate their answer first.
- If they are asking a new question, follow the 'DeepStudy Coach' structure: Analogy, Connection, Breakdown, The Trap, and Challenge.
"""
        
        explanation = llm_client.chat(
            system_prompt=system_prompt,
            user_message=full_user_msg,
            json_mode=False 
        )

        return repair_text + explanation
