import os
from dotenv import load_dotenv
from google import genai
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointInsertOperations, PointStruct
from qdrant_client.http import models

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API"))
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API")
)
collectionName = "document_collection"


class VectorDocument:
    def __init__(self, name, content, summary=""):
        self.name = name
        self.content = content
        self.summary = summary

    def createEmbedding(self):
        results = gemini_client.models.embed_content(
            model=os.getenv("GEMINI_MODEL"), contents=self.content
        )
        self.embeddings = results.embeddings[0].values

    def storeEmbedding(self, id):
        collectionInfo = qdrant_client.get_collection(collectionName)
        qdrant_client.upsert(
            collection_name=collectionName,
            points=[
                PointStruct(
                    id=id, vector=self.embeddings, payload={"content": self.content}
                )
            ],
        )
