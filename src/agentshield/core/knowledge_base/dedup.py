"""
dedup.py
--------

STEP 4 of the RAG pipeline:
Semantic Deduplication

Purpose:
    Remove near-duplicate document chunks before generating
    embeddings and storing them in Qdrant.

Workflow:

    Chunk Documents
          ↓
    Generate Embeddings
          ↓
    Cosine Similarity
          ↓
    Remove Near Duplicates
          ↓
    Return Unique Chunks
"""

from typing import List

import numpy as np
from langchain_core.documents import Document
from sklearn.metrics.pairwise import cosine_similarity

from .config import SEMANTIC_DEDUP_THRESHOLD
from .embeddings import embed_texts


def semantic_deduplicate(
    chunks: List[Document],
    threshold: float = SEMANTIC_DEDUP_THRESHOLD,
) -> List[Document]:
    """
    Remove semantically similar chunks using cosine similarity.

    Parameters
    ----------
    chunks:
        List of LangChain Documents.

    threshold:
        Cosine similarity threshold.
        Higher values remove fewer chunks.

    Returns
    -------
    List[Document]
        Deduplicated documents.
    """

    if len(chunks) <= 1:
        return chunks

    texts = [
        chunk.page_content
        for chunk in chunks
    ]

    embeddings = np.asarray(
        embed_texts(texts),
        dtype=np.float32,
    )

    kept_documents: List[Document] = []
    kept_embeddings: List[np.ndarray] = []

    removed = 0

    for chunk, embedding in zip(chunks, embeddings):

        if not kept_embeddings:
            kept_documents.append(chunk)
            kept_embeddings.append(embedding)
            continue

        similarities = cosine_similarity(
            embedding.reshape(1, -1),
            np.stack(kept_embeddings),
        )[0]

        if similarities.max() >= threshold:
            removed += 1
            continue

        kept_documents.append(chunk)
        kept_embeddings.append(embedding)

    print(
        f"[dedup] Removed {removed} duplicate chunk(s). "
        f"Remaining: {len(kept_documents)}"
    )

    return kept_documents


if __name__ == "__main__":

    docs = [
        Document(
            page_content="Enable S3 Block Public Access for all buckets."
        ),
        Document(
            page_content="S3 buckets should have Block Public Access enabled."
        ),
        Document(
            page_content="Rotate KMS keys annually."
        ),
    ]

    unique_docs = semantic_deduplicate(docs)

    print("\nUnique Documents\n")

    for index, doc in enumerate(unique_docs, start=1):
        print(f"{index}. {doc.page_content}")