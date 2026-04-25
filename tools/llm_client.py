import os
import json
from typing import Optional, Dict, Any, Union
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class LLMClient:
    """
    Unified client for interacting with Gemini via Vertex AI.
    Handles authentication, system prompts, and structured JSON output.
    """
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.model_name = "gemini-2.5-flash"  # Using the latest Gen 2.5 model
        
        # Initialize the Modern GenAI Client for Vertex AI
        self.client = genai.Client(
            vertexai=True,
            project=self.project_id,
            location=self.location
        )

    def chat(self, 
             system_prompt: str, 
             user_message: str, 
             json_mode: bool = False,
             temperature: float = 0.2) -> Union[str, Dict[str, Any]]:
        """
        Sends a message to Gemini and returns the response.
        """
        config = {
            "system_instruction": system_prompt,
            "temperature": temperature,
        }

        # If JSON mode is requested, force the output format
        if json_mode:
            config["response_mime_type"] = "application/json"

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_message,
                config=types.GenerateContentConfig(**config)
            )

            if json_mode:
                # Parse and return as a Python dictionary
                return json.loads(response.text)
            
            return response.text

        except Exception as e:
            print(f"Error calling LLM: {str(e)}")
            # Return an empty dict or error message so the pipeline doesn't crash
            return {} if json_mode else f"Error: {str(e)}"

# Singleton instance for easy importing across the project
llm_client = LLMClient()
