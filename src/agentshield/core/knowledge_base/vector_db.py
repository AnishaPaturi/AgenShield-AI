"""
vector_db.py
------------
STEP 5 of the RAG pipeline: Vector Database (Qdrant).

Purpose:
    Build the AgentShield-AI knowledge base by:
        1. Loading PDFs (and scraped content)
        2. Chunking documents
        3. De-duplicating near-identical chunks
        4. Creating embeddings
        5. Storing vectors inside Qdrant
"""

import hashlib
from typing import Any, Dict, List

from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from .dedup import semantic_deduplicate
from .config import (
    COLLECTION_NAME,
    EMBEDDING_DIM,
    QDRANT_PATH,
    VECTOR_BATCH_SIZE,
)
from .embeddings import embed_texts


def get_client() -> QdrantClient:
    """
    Create or connect to the local Qdrant database.
    """

    return QdrantClient(path=str(QDRANT_PATH))


def create_collection(client: QdrantClient) -> None:
    """
    Create the vector collection if it does not already exist.
    """

    existing = [
        collection.name
        for collection in client.get_collections().collections
    ]

    if COLLECTION_NAME in existing:
        print(
            f"[vector_db] Collection '{COLLECTION_NAME}' already exists."
        )
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=qmodels.VectorParams(
            size=EMBEDDING_DIM,
            distance=qmodels.Distance.COSINE,
        ),
    )

    print(
        f"[vector_db] Created collection "
        f"'{COLLECTION_NAME}' "
        f"(dimension={EMBEDDING_DIM})"
    )


def upsert_chunks(
    client: QdrantClient,
    chunks: List[Document],
    batch_size: int = VECTOR_BATCH_SIZE,
    dedup: bool = True,
) -> None:
    """
    Optionally de-duplicate, then embed document chunks and store
    them inside Qdrant.
    """

    if dedup:
        chunks = semantic_deduplicate(chunks)

    if not chunks:
        print("[vector_db] Nothing to upsert after dedup.")
        return

    for start in range(0, len(chunks), batch_size):

        batch = chunks[start : start + batch_size]

        texts = [chunk.page_content for chunk in batch]

        vectors = embed_texts(texts)

        points = []

        for chunk, vector in zip(batch, vectors):

            chunk_key = chunk.metadata.get(
                "chunk_id",
                chunk.page_content,
            )

            point_id = int(
                hashlib.md5(
                    chunk_key.encode("utf-8")
                ).hexdigest()[:16],
                16,
            )

            point = qmodels.PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "text": chunk.page_content,
                    **chunk.metadata,
                },
            )

            points.append(point)

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

        print(
            f"[vector_db] "
            f"Upserted {start + len(batch)}/{len(chunks)} chunks"
        )


def fetch_all_payloads(client: QdrantClient) -> List[Dict[str, Any]]:
    """
    Scroll through every point in the collection and return its
    payload. Used by hybrid_search.py to build the sparse/lexical
    index from the same corpus that's stored in Qdrant, so dense and
    sparse search always stay in sync.
    """

    all_payloads: List[Dict[str, Any]] = []
    next_offset = None

    while True:

        points, next_offset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=256,
            offset=next_offset,
            with_payload=True,
            with_vectors=False,
        )

        all_payloads.extend(point.payload for point in points)

        if next_offset is None:
            break

    return all_payloads


def build_knowledge_base() -> QdrantClient:
    """
    Build the complete AgentShield-AI knowledge base from PDFs and
    any scraped content, then (re)build the BM25 sparse index so
    hybrid search is ready to go.
    """

    from .chunker import chunk_documents
    from .loaders import load_all_documents, load_all_scraped

    print("[vector_db] STEP 1/4 : Loading PDFs + scraped content")
    documents = load_all_documents() + load_all_scraped()

    print("[vector_db] STEP 2/4 : Chunking")
    chunks = chunk_documents(documents)

    print("[vector_db] STEP 3/4 : Deduplicating + embedding + storing")

    client = get_client()

    create_collection(client)

    upsert_chunks(client, chunks)

    print("[vector_db] STEP 4/4 : Building BM25 sparse index")

    from .hybrid_search import build_bm25_index

    build_bm25_index(client)

    print(
        f"\n[vector_db] Knowledge Base built successfully "
        f"({len(chunks)} chunks)"
    )

    return client


if __name__ == "__main__":
    build_knowledge_base()