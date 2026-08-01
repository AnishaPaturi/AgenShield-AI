"""
retriever.py
------------
STEP 6a of the RAG pipeline: Dense Semantic Retrieval.

Purpose:
    Search Qdrant for the chunks whose embeddings are most similar
    to the query embedding. This is the "dense" half of hybrid
    search — see hybrid_search.py for how this gets combined with
    BM25 sparse (keyword) search.

Workflow:
    User Query
        ↓
    Generate Query Embedding
        ↓
    Apply Optional Metadata Filters
        ↓
    Dense Vector Search (Qdrant)
        ↓
    Return Top-K Most Relevant Chunks
"""

from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from .config import (
    COLLECTION_NAME,
    DEFAULT_TOP_K,
)
from .embeddings import embed_query
from .vector_db import get_client


def dense_search(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    category_filter: Optional[str] = None,
    folder_filter: Optional[str] = None,
    compliance_control: Optional[str] = None,
    client: Optional[QdrantClient] = None,
) -> List[Dict[str, Any]]:
    """
    Perform dense semantic similarity search on the knowledge base.

    Parameters
    ----------
    query:
        User query.

    top_k:
        Number of results to return.

    category_filter:
        Optional metadata filter.

    folder_filter:
        Restrict search to a particular folder
        (aws, azure, gcp, terraform...)

    compliance_control:
        Restrict retrieval to a specific compliance control
        (NIST-AC-6, PCI-DSS-1.3, etc.)

    client:
        Existing Qdrant client.
        If None, a new local client is created.

    Returns
    -------
    List[Dict]
        Top-K semantically relevant chunks ordered by similarity score.
    """

    if client is None:
        client = get_client()

    query_vector = embed_query(query)

    conditions = []

    if category_filter:
        conditions.append(
            qmodels.FieldCondition(
                key="category",
                match=qmodels.MatchValue(value=category_filter),
            )
        )

    if folder_filter:
        conditions.append(
            qmodels.FieldCondition(
                key="folder",
                match=qmodels.MatchValue(value=folder_filter),
            )
        )

    if compliance_control:
        conditions.append(
            qmodels.FieldCondition(
                key="compliance_controls",
                match=qmodels.MatchValue(value=compliance_control),
            )
        )

    query_filter = (
        qmodels.Filter(must=conditions)
        if conditions
        else None
    )

    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        query_filter=query_filter,
        with_payload=True,
    )

    results = []

    for hit in response.points:

        results.append(
            {
                "score": hit.score,
                "text": hit.payload.get("text"),
                "source_file": hit.payload.get("source_file"),
                "folder": hit.payload.get("folder"),
                "category": hit.payload.get("category"),
                "page": hit.payload.get("page"),
                "compliance_controls": hit.payload.get(
                    "compliance_controls",
                    [],
                ),
                "compliance_frameworks": hit.payload.get(
                    "compliance_frameworks",
                    [],
                ),
            }
        )

    return results


if __name__ == "__main__":

    query = "public S3 bucket security misconfiguration"

    results = dense_search(
        query=query,
        top_k=3,
    )

    print("\n========== DENSE RETRIEVAL RESULTS ==========\n")

    if not results:
        print("No matching documents found.")

    for result in results:

        print(f"Score : {result['score']:.4f}")
        print(f"Source: {result['source_file']}")
        print(f"Folder: {result['folder']}")
        print(f"Page  : {result['page']}")
        print()

        print((result["text"] or "")[:250])

        print("\n" + "-" * 80)