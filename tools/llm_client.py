import os
import json
import time
from typing import Optional, Dict, Any, Union
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class LLMClient:
    """
    Unified client for interacting with Gemini via Vertex AI.
    Optimized for Gemini 2.5 with explicit timeouts and retry logic.
    """
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        # Ensure we use the verified location
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.model_name = "gemini-2.5-flash"
        
        # Initialize client with a strict 30s timeout for the whole request
        self.client = genai.Client(
            vertexai=True,
            project=self.project_id,
            location=self.location,
            http_options={'timeout': 30000} # 30 seconds in milliseconds
        )

    def chat(self, 
             system_prompt: str, 
             user_message: str, 
             json_mode: bool = False,
             temperature: float = 0.2,
             max_retries: int = 2) -> Union[str, Dict[str, Any]]:
        
        # Combine system prompt into user message as a fallback for 2.5 stability
        combined_message = f"INSTRUCTIONS:\n{system_prompt}\n\nUSER INPUT:\n{user_message}"
        
        config = {
            "temperature": temperature,
        }

        if json_mode:
            config["response_mime_type"] = "application/json"

        for attempt in range(max_retries):
            try:
                print(f"   [LLM] Calling {self.model_name} (Attempt {attempt+1})...")
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=combined_message,
                    config=types.GenerateContentConfig(**config)
                )

                if not response or not response.text:
                    print("   ⚠️ Empty response. Retrying...")
                    continue

                if json_mode:
                    try:
                        # Strip markdown code blocks if the model accidentally includes them
                        clean_text = response.text.replace("```json", "").replace("```", "").strip()
                        return json.loads(clean_text)
                    except json.JSONDecodeError:
                        print("   ⚠️ Invalid JSON. Retrying...")
                        continue
                
                return response.text

            except Exception as e:
                print(f"   ❌ LLM Attempt {attempt+1} failed: {str(e)}")
                if "429" in str(e):
                    print("   ⏳ Rate limit hit. Waiting 5 seconds...")
                    time.sleep(5)
                elif attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    break

        return {} if json_mode else "Connection error. Please check your network or API quota."

llm_client = LLMClient()
