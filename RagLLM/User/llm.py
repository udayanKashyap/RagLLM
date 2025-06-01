from logging import warning
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
        self.collectionInfo = qdrantClient.get_collection(collectionName)

    def createEmbedding(self):
        results = geminiClient.models.embed_content(
            model=os.getenv("GEMINI_MODEL"), contents=self.content
        )
        self.embeddings = results.embeddings[0].values

    def storeEmbedding(self):
        if self.embeddings is None:
            raise Http404
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


class VectorData:
    def __init__(self, embeddings=[], content=""):
        self.content = content
        self.embeddings = embeddings
        self.collectionInfo = qdrantClient.get_collection(collectionName)

    def getNextId(self):
        return self.collectionInfo.points_count

    def createEmbedding(self):
        if len(self.embeddings) > 0:
            print("\nEMBEDDING ALREADY EXISTS\n")
            raise warning("Embedding already exists")
        results = geminiClient.models.embed_content(
            model=os.getenv("GEMINI_MODEL"), contents=self.content
        )
        self.embeddings = results.embeddings[0].values
        return self.embeddings

    def storeEmbedding(self):
        if self.embeddings is None:
            raise Http404
        qdrantClient.upsert(
            collection_name=collectionName,
            points=[
                PointStruct(
                    id=self.getNextId(),
                    vector=self.embeddings,
                    payload={"content": self.content},
                )
            ],
        )

    def getSimilarContent(self, k=5):
        if not self.embeddings:
            raise ValueError("Embeddings not set")
        search_results = qdrantClient.search(
            collection_name=collectionName,
            query_vector=self.embeddings,
            limit=k,
            with_payload=True,
            with_vectors=False,
        )
        similar_content = [
            {
                "content": hit.payload.get("content", ""),
                "score": hit.score,
                "id": hit.id,
            }
            for hit in search_results
        ]
        return similar_content

    def __str__(self) -> str:
        return f"filename: {self.name}, summary: {self.summary}"
