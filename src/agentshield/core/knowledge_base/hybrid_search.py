"""
hybrid_search.py
-----------------
STEP 6b of the RAG pipeline: Hybrid Retrieval (Task 2.4).

Purpose:
    Combine dense vector similarity (Qdrant, via retriever.dense_search)
    with sparse BM25 keyword search into a single ranked result list.

Workflow:
    User Query
          ↓
    Dense Retrieval (Qdrant)
          ↓
    Sparse Retrieval (BM25)
          ↓
    Reciprocal Rank Fusion (RRF)
          ↓
    Metadata Filtering
          ↓
    Final Ranked Results
"""

import pickle
import re
from typing import Any, Dict, List, Optional, Tuple

from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi

from .config import (
    BM25_INDEX_FILE,
    DEFAULT_TOP_K,
    DENSE_WEIGHT,
    SPARSE_WEIGHT,
    RRF_K,
    DENSE_POOL,
    SPARSE_POOL,
)
from .retriever import dense_search


# =============================================================================
# BM25 INDEX
# =============================================================================


def _tokenize(text: str) -> List[str]:
    """
    Lightweight tokenizer for BM25.
    """

    return re.findall(
        r"[a-z0-9][a-z0-9._-]*",
        text.lower(),
    )


def build_bm25_index(client: QdrantClient) -> None:
    """
    Build and persist the BM25 index from the current Qdrant collection.
    """

    from .vector_db import fetch_all_payloads

    payloads = fetch_all_payloads(client)

    if not payloads:
        print(
            "[hybrid_search] No payloads found in Qdrant."
        )
        return

    corpus = [
        payload.get("text", "")
        for payload in payloads
    ]

    tokenized = [
        _tokenize(text)
        for text in corpus
    ]

    bm25 = BM25Okapi(tokenized)

    with open(BM25_INDEX_FILE, "wb") as f:

        pickle.dump(
            {
                "bm25": bm25,
                "payloads": payloads,
            },
            f,
        )

    print(
        f"[hybrid_search] Built BM25 index "
        f"({len(payloads)} chunks)"
    )


def load_bm25_index() -> Dict[str, Any]:
    """
    Load BM25 index from disk.
    """

    if not BM25_INDEX_FILE.exists():

        raise FileNotFoundError(
            f"{BM25_INDEX_FILE} not found."
        )

    with open(BM25_INDEX_FILE, "rb") as f:

        return pickle.load(f)


def bm25_search(
    query: str,
    top_k: int = DEFAULT_TOP_K,
) -> List[Tuple[Dict[str, Any], float]]:
    """
    Run BM25 search.
    """

    index = load_bm25_index()

    bm25 = index["bm25"]

    payloads = index["payloads"]

    scores = bm25.get_scores(
        _tokenize(query)
    )

    ranked = sorted(
        zip(payloads, scores),
        key=lambda x: x[1],
        reverse=True,
    )

    return ranked[:top_k]


# =============================================================================
# HYBRID SEARCH
# =============================================================================


def _payload_to_result(
    payload: Dict[str, Any],
    score: float,
) -> Dict[str, Any]:

    return {
        "score": score,
        "text": payload.get("text"),
        "source_file": payload.get("source_file"),
        "folder": payload.get("folder"),
        "category": payload.get("category"),
        "page": payload.get("page"),
        "compliance_controls": payload.get(
            "compliance_controls",
            [],
        ),
        "compliance_frameworks": payload.get(
            "compliance_frameworks",
            [],
        ),
    }


def _chunk_key(
    result: Dict[str, Any],
) -> str:

    return (
        f"{result.get('source_file')}::"
        f"{(result.get('text') or '')[:80]}"
    )


def hybrid_search(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    category_filter: Optional[str] = None,
    folder_filter: Optional[str] = None,
    compliance_control: Optional[str] = None,
    dense_pool: int = DENSE_POOL,
    sparse_pool: int = SPARSE_POOL,
) -> List[Dict[str, Any]]:
    """
    Hybrid retrieval using:

        Dense Search
            +
        BM25
            +
        Reciprocal Rank Fusion
    """

    dense_results = dense_search(
        query=query,
        top_k=dense_pool,
        category_filter=category_filter,
        folder_filter=folder_filter,
        compliance_control=compliance_control,
    )

    try:

        sparse_hits = bm25_search(
            query=query,
            top_k=sparse_pool,
        )

        sparse_results = [
            _payload_to_result(payload, score)
            for payload, score in sparse_hits
        ]

    except FileNotFoundError:

        print(
            "[hybrid_search] "
            "BM25 index missing. "
            "Using dense retrieval only."
        )

        sparse_results = []

    fused_scores: Dict[str, float] = {}

    fused_payloads: Dict[str, Dict[str, Any]] = {}

    for rank, result in enumerate(dense_results):

        key = _chunk_key(result)

        fused_scores[key] = (
            fused_scores.get(key, 0.0)
            + DENSE_WEIGHT / (RRF_K + rank + 1)
        )

        fused_payloads[key] = result

    for rank, result in enumerate(sparse_results):

        if (
            category_filter
            and result.get("category") != category_filter
        ):
            continue

        if (
            folder_filter
            and result.get("folder") != folder_filter
        ):
            continue

        if (
            compliance_control
            and compliance_control
            not in result.get(
                "compliance_controls",
                [],
            )
        ):
            continue

        key = _chunk_key(result)

        fused_scores[key] = (
            fused_scores.get(key, 0.0)
            + SPARSE_WEIGHT / (RRF_K + rank + 1)
        )

        fused_payloads.setdefault(
            key,
            result,
        )

    ranked = sorted(
        fused_scores,
        key=lambda k: fused_scores[k],
        reverse=True,
    )

    results = []

    for key in ranked[:top_k]:

        result = dict(
            fused_payloads[key]
        )

        result["score"] = fused_scores[key]

        results.append(result)

    return results


if __name__ == "__main__":

    query = "public S3 bucket security misconfiguration"

    results = hybrid_search(
        query=query,
        top_k=3,
    )

    print(
        "\n========== HYBRID RETRIEVAL RESULTS ==========\n"
    )

    if not results:

        print("No matching documents found.")

    for result in results:

        print(
            f"Score : {result['score']:.4f}"
        )

        print(
            f"Source: {result['source_file']}"
        )

        print(
            f"Folder: {result['folder']}"
        )

        print(
            f"Page  : {result['page']}"
        )

        print(
            f"Controls: {result['compliance_controls']}"
        )

        print()

        print(
            (result["text"] or "")[:250]
        )

        print("\n" + "-" * 80)