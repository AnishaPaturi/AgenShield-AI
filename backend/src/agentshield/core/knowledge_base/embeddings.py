"""
embeddings.py
-------------
STEP 4 of the RAG pipeline: Embedding Generation.

Purpose:
    Convert chunks of text into dense numerical vectors using a
    Sentence Transformer model.

Why embeddings?
    Similar pieces of text are mapped to nearby points in vector
    space, enabling semantic search instead of keyword matching.

Model:
    Configurable via config.EMBEDDING_MODEL_NAME (default:
    sentence-transformers/all-mpnet-base-v2, 768-dim). BGE models
    are also supported and get their recommended query prefix
    applied automatically.
"""

from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from .config import BGE_QUERY_PREFIX, EMBEDDING_DIM, EMBEDDING_MODEL_NAME

MODEL_NAME = EMBEDDING_MODEL_NAME

# Lazy-loaded singleton model
_model: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    """
    Load the embedding model once and reuse it throughout the application.
    """
    global _model

    if _model is None:
        print(f"[embeddings] Loading model: {MODEL_NAME} (dim={EMBEDDING_DIM})")
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Convert a list of text chunks into embedding vectors.

    Args:
        texts: List of strings.

    Returns:
        List of embedding vectors.
    """

    model = get_embedding_model()

    vectors = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=len(texts) > 32,
        normalize_embeddings=True,
    )

    return vectors.tolist()


def embed_query(query: str) -> List[float]:
    """
    Embed a user query using the same embedding model.

    Using the same model for both documents and queries ensures
    they live in the same vector space. BGE models are trained to
    expect an instruction prefix on the *query* side only.
    """

    if MODEL_NAME.lower().startswith("baai/bge"):
        query = BGE_QUERY_PREFIX + query

    return embed_texts([query])[0]


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Cosine similarity between two already-normalized embedding
    vectors. Since embed_texts normalizes vectors, this reduces to a
    dot product, but we compute it defensively in case a caller
    passes in un-normalized vectors.
    """

    a = np.array(vec_a)
    b = np.array(vec_b)

    denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1e-8

    return float(np.dot(a, b) / denom)


if __name__ == "__main__":

    sample_texts = [
        "Public S3 bucket exposes data.",
        "Open storage bucket leaks information.",
        "The cat sat on the mat.",
    ]

    vectors = embed_texts(sample_texts)

    print(f"\nEmbedding Dimension: {len(vectors[0])}")

    print(
        f"Cosine Similarity (related): "
        f"{cosine_similarity(vectors[0], vectors[1]):.4f}"
    )

    print(
        f"Cosine Similarity (unrelated): "
        f"{cosine_similarity(vectors[0], vectors[2]):.4f}"
    )