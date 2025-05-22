import os
from django.http import Http404
from dotenv import load_dotenv
from google import genai
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointInsertOperations, PointStruct
from qdrant_client.http import models

from RagLLM import qdrantClient, geminiClient

# gemini_client = genai.Client(api_key=os.getenv("GEMINI_API"))
# qdrant_client = QdrantClient(
#     url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API")
# )
collectionName = "document_collection"


class VectorDocument:
    def __init__(self, id, name, content, summary=""):
        self.id = id
        self.name = name
        self.content = content
        self.summary = summary
        self.embeddings = None

    def createEmbedding(self):
        results = geminiClient.models.embed_content(
            model=os.getenv("GEMINI_MODEL"), contents=self.content
        )
        self.embeddings = results.embeddings[0].values

    def storeEmbedding(self):
        if self.embeddings is None:
            raise Http404
        collectionInfo = qdrantClient.get_collection(collectionName)
        qdrantClient.upsert(
            collection_name=collectionName,
            points=[
                PointStruct(
                    id=self.id,
                    vector=self.embeddings,
                    payload={"content": self.content},
                )
            ],
        )

    def __str__(self) -> str:
        return f"filename: {self.name}, summary: {self.summary}"
