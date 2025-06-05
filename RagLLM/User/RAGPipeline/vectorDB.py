import uuid
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from textSegmentation import ChunkData
from RagLLM import qdrantClient, geminiClient


def upload_to_qdrant(
    chunk_data_list: List[ChunkData],
    collection_name: str,
) -> bool:
    """
    Upload chunks to Qdrant vector database

    Args:
        chunk_data_list: List of ChunkData objects
        collection_name: Name of the Qdrant collection

    Returns:
        Boolean indicating success
    """
    try:
        # Create collection if it doesn't exist
        if not qdrantClient.collection_exists(collection_name):
            vector_size = len(chunk_data_list[0].embedding_vector)
            qdrantClient.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

        # Prepare points for upload
        points = []
        for chunk in chunk_data_list:
            # Metadata payload (everything except the vector)
            payload = {
                "chunk_id": chunk.chunk_id,
                "source_document": chunk.source_document,
                "text_content": chunk.text_content,
                "chunk_position": chunk.chunk_position,
                "token_count": chunk.token_count,
                "creation_timestamp": chunk.creation_timestamp,
            }

            # Create point with vector and payload
            point = PointStruct(
                id=chunk.chunk_id, vector=chunk.embedding_vector, payload=payload
            )
            points.append(point)

        # Upload points to Qdrant
        operation_info = qdrantClient.upsert(
            collection_name=collection_name, points=points
        )

        print(
            f"Successfully uploaded {len(points)} chunks to Qdrant collection '{collection_name}'"
        )
        return True

    except Exception as e:
        print(f"Error uploading to Qdrant: {str(e)}")
        return False
