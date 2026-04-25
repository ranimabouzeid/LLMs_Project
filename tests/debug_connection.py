import os
import time
from dotenv import load_dotenv
from google import genai

def debug_connection():
    load_dotenv()
    # FORCE the settings that worked during list_models.py
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = "us-central1" # Hardcoding for this test
    model_name = "gemini-2.5-flash"

    print(f"🚀 DEBUG: Testing Vertex AI in {location}...")
    print(f"   - Project: {project_id}")
    print(f"   - Model: {model_name}")

    try:
        client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location
        )
        
        print("\n⏳ Sending request... (Timing out in 20s if no response)")
        
        # This is a basic call to see if the pipe is open
        response = client.models.generate_content(
            model=model_name,
            contents="Hello"
        )
        
        print("\n✅ SUCCESS!")
        print(f"🤖 Response: {response.text}")

    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")

if __name__ == "__main__":
    debug_connection()
