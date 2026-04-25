import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

if not project_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT is missing in .env")

client = genai.Client(
    vertexai=True,
    project=project_id,
    location=location,
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say only: Gemini 2.5 Flash Vertex AI connection works."
)

print(response.text)