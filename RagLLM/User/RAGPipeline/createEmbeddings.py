import uuid
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from torch import embedding
from textSegmentation import ChunkData


def create_batch_embeddings(
    chunks: List[Dict],
    task_description: str = "Given a question, retrieve document passages that answer the question",
) -> List[ChunkData]:
    """
    Create batch embeddings for text chunks using linq-embed-mistral

    Args:
        chunks: List of chunk dictionaries
        task_description: Task instruction for the embedding model

    Returns:
        List of ChunkData objects with embeddings
    """
    # Initialize the linq-embed-mistral model
    model = SentenceTransformer("Linq-AI-Research/Linq-Embed-Mistral")

    # Extract text content for batch embedding
    passages = [chunk["text_content"] for chunk in chunks]

    # Generate embeddings for passages (no prompt needed for passages)
    embeddings = model.encode(passages, batch_size=32, show_progress_bar=True)

    # Create ChunkData objects with embeddings
    chunk_data_list = []
    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding_vector"] = embedding.tolist()
        chunk_data = ChunkData(
            chunk_id=chunk["chunk_id"],
            source_document=chunk["source_document"],
            text_content=chunk["text_content"],
            embedding_vector=chunk["embedding_vector"],
            chunk_position=chunk["chunk_position"],
            token_count=chunk["token_count"],
            creation_timestamp=chunk["creation_timestamp"],
        )
        chunk_data_list.append(chunk_data)

    return chunk_data_list


def encode_queries_for_retrieval(
    query: str,
    task_description: str = "Given a question, retrieve document passages that answer the question",
) -> List[float]:
    """
    Encode query for retrieval using linq-embed-mistral with task instruction

    Args:
        query: query string
        task_description: Task instruction for the embedding model

    Returns:
        Embedded query vector
    """
    # Initialize the linq-embed-mistral model
    model = SentenceTransformer("Linq-AI-Research/Linq-Embed-Mistral")

    # Create prompt with task instruction
    prompt = f"Instruct: {task_description}\nQuery: "

    # Generate embeddings for queries with prompt
    embedding = model.encode(query, prompt=prompt)

    return embedding.tolist()
