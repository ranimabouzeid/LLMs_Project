from typing import List
from tools.llm_client import llm_client
from pipeline.prompts import DECOMPOSER_SYSTEM_PROMPT
from pipeline.schemas import KeyIdea

class Decomposer:
    """
    Agent responsible for breaking down a topic into its constituent must-understand concepts.
    """
    def __init__(self):
        self.system_prompt = DECOMPOSER_SYSTEM_PROMPT

    def decompose(self, topic: str) -> List[KeyIdea]:
        """
        Calls Gemini to extract key ideas and returns a list of KeyIdea objects.
        """
        user_msg = f"Decompose the following topic into its essential sub-concepts: {topic}"
        
        # Use json_mode=True to get a dictionary back automatically
        response_data = llm_client.chat(
            system_prompt=self.system_prompt,
            user_message=user_msg,
            json_mode=True
        )

        key_ideas = []
        # Extract the list from the JSON key "key_ideas"
        raw_ideas = response_data.get("key_ideas", [])

        for idea in raw_ideas:
            # Validate using our Pydantic schema
            key_ideas.append(KeyIdea(
                name=idea.get("name", "Unknown Concept"),
                description=idea.get("description", "")
            ))

        return key_ideas
