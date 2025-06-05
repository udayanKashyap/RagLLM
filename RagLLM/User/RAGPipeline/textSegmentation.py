import uuid
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


class ChunkData:
    chunk_id: str
    source_document: str
    text_content: str
    embedding_vector: List[float]
    chunk_position: int
    token_count: int
    creation_timestamp: str


def createSegments(
    text: str,
    tokens: int = 512,
    overlap: int = 50,
    source_document: str = "unknown.pdf",
) -> List[Dict]:
    """
    Create text segments using LangChain's RecursiveCharacterTextSplitter

    Args:
        text: Input text to segment
        tokens: Maximum tokens per chunk
        overlap: Token overlap between chunks
        source_document: Source document name
        page_number: Page number in the document

    Returns:
        List of chunk dictionaries with metadata
    """
    # Initialize tokenizer (using GPT-3.5-turbo encoding as default)
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def token_length(text: str) -> int:
        return len(encoding.encode(text))

    # Create text splitter with token-based splitting
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=tokens,
        chunk_overlap=overlap,
        length_function=token_length,
        separators=["\n\n", "\n", " ", ""],
    )

    # Split the text
    chunks = text_splitter.split_text(text)

    # Create structured chunks
    segments = []
    for i, chunk in enumerate(chunks):
        chunk_data = {
            "chunk_id": str(uuid.uuid4()),
            "source_document": source_document,
            "text_content": chunk,
            "embedding_vector": [],  # Will be filled by embedding function
            "chunk_position": i + 1,
            "token_count": token_length(chunk),
            "creation_timestamp": datetime.utcnow().isoformat() + "Z",
        }
        segments.append(chunk_data)

    return segments
