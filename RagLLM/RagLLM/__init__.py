import os
from google import genai
from qdrant_client import QdrantClient


geminiClient = genai.Client(api_key=os.getenv("GEMINI_API"))
qdrantClient = QdrantClient(
    url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API")
)
