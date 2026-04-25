from typing import List, Optional
from tools.llm_client import llm_client
from pipeline.prompts import EXPLANATION_SYSTEM_PROMPT
from pipeline.schemas import KeyIdea, Chunk, DebtEntry

class ExplanationAgent:
    """
    The main agent responsible for generating the structured pedagogical response.
    """
    def __init__(self):
        self.system_prompt = EXPLANATION_SYSTEM_PROMPT

    def generate_explanation(self, 
                             query: str, 
                             key_ideas: List[KeyIdea], 
                             approved_chunks: List[Chunk], 
                             open_debts: List[DebtEntry] = []) -> str:
        """
        Generates a deep explanation using the approved chunks and addressing key ideas.
        If open_debts are provided, it prepends a 'Prerequisite Repair' section.
        """
        
        # 1. Build the context from retrieved chunks
        context_text = "\n\n".join([f"[Source: {c.metadata.get('source', 'Unknown')}] {c.text}" for c in approved_chunks])
        
        # 2. Build the list of must-cover ideas
        ideas_text = "\n".join([f"- {i.name}: {i.description}" for i in key_ideas])
        
        # 3. Handle Prerequisite Repairs (The CDL logic)
        repair_text = ""
        if open_debts:
            repair_text = "### 🛠️ Prerequisite Foundations\n"
            repair_text += "Before we dive in, let's quickly clarify some concepts you struggled with recently:\n"
            for debt in open_debts:
                repair_text += f"- {debt.prerequisite_concept}: (Briefly explained based on your history)\n"
            repair_text += "\n---\n\n"

        # 4. Construct the final prompt
        full_user_msg = f"""
STUDENT QUESTION: {query}

ESSENTIAL KEY IDEAS TO COVER:
{ideas_text}

SOURCE MATERIAL (Use ONLY these facts):
{context_text}

INSTRUCTIONS:
Generate a response following the 'DeepStudy Coach' structure: Analogy, Connection, Breakdown, The Trap, and Challenge.
"""
        
        # We don't use JSON mode here because we want a rich, formatted Markdown explanation.
        explanation = llm_client.chat(
            system_prompt=self.system_prompt,
            user_message=full_user_msg,
            json_mode=False 
        )

        return repair_text + explanation
