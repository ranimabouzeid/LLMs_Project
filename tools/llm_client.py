import os
import json
import time
import random
from typing import Optional, Dict, Any, Union, Generator
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class LLMClient:
    """
    Unified client for interacting with Gemini via Vertex AI.
    Optimized for Gemini 2.5 with Jitter-based retries to survive 429 limits.
    """
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        # Pull from ENV or default to us-central1 for stability if needed
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.model_name = "gemini-2.5-flash"
        
        self.client = genai.Client(
            vertexai=True,
            project=self.project_id,
            location=self.location,
            http_options={'timeout': 60000}
        )

    def stream_chat(self, 
                    system_prompt: str, 
                    user_message: str, 
                    temperature: float = 0.2) -> Generator[str, None, None]:
        combined_message = f"INSTRUCTIONS:\n{system_prompt}\n\nUSER INPUT:\n{user_message}"
        config = {"temperature": temperature}
        try:
            for chunk in self.client.models.generate_content_stream(
                model=self.model_name,
                contents=combined_message,
                config=types.GenerateContentConfig(**config)
            ):
                if chunk.text: yield chunk.text
        except Exception as e:
            yield f"\n⚠️ [Stream Error]: {str(e)}"

    def chat(self, 
             system_prompt: str, 
             user_message: str, 
             json_mode: bool = False,
             temperature: float = 0.2,
             max_retries: int = 3) -> Union[str, Dict[str, Any]]:
        
        combined_message = f"INSTRUCTIONS:\n{system_prompt}\n\nUSER INPUT:\n{user_message}"
        config = {"temperature": temperature}
        if json_mode: config["response_mime_type"] = "application/json"

        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=combined_message,
                    config=types.GenerateContentConfig(**config)
                )

                if response and response.text:
                    if json_mode:
                        clean_text = response.text.replace("```json", "").replace("```", "").strip()
                        return json.loads(clean_text)
                    return response.text
            except Exception as e:
                if "429" in str(e):
                    # JITTER: Wait 10s + random small amount so parallel tasks don't collide
                    wait_time = 10 + random.uniform(1, 5)
                    print(f"   ⏳ Quota hit. Attempt {attempt+1} failed. Backing off for {round(wait_time, 1)}s...")
                    time.sleep(wait_time)
                else:
                    time.sleep(2)

        return {} if json_mode else "Connection error. Please try again in a moment."

llm_client = LLMClient()
