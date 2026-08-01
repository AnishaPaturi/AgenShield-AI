"""
rag.py
------
STEP 7 of the RAG pipeline: Retrieval-Augmented Generation (RAG).

Purpose:
    Retrieve the most relevant document chunks from the knowledge
    base and assemble them into a context block — annotated with
    compliance control IDs — that Member 3's Security Analyst Agent
    can drop straight into its working memory / prompt.

Pipeline:
    User Query
        ↓
    Embed Query + Tokenize Query
        ↓
    Hybrid Search (Qdrant dense + BM25 sparse, RRF fusion)
        ↓
    Top-K Relevant Chunks
        ↓
    Context Assembly (+ compliance control tagging)
        ↓
    Prompt Generation
        ↓
    Member 3's LLM
"""

from typing import Any, Dict, List

from .config import DEFAULT_TOP_K
from .hybrid_search import hybrid_search


def build_context(results: List[Dict[str, Any]]) -> str:
    """
    Build a readable context block from retrieved chunks.
    Each chunk is tagged with its source and any compliance control
    IDs it maps to, for traceability.
    """

    blocks = []

    for index, result in enumerate(results, start=1):

        source = result.get("source_file", "Unknown")
        page = result.get("page", "N/A")
        text = result.get("text", "")
        controls = result.get("compliance_controls") or []

        control_tag = f" | Controls: {', '.join(controls)}" if controls else ""

        block = (
            f"[Source {index}: {source}, page {page}{control_tag}]\n"
            f"{text}"
        )

        blocks.append(block)

    return "\n\n".join(blocks)


def retrieve_context(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    **filters,
) -> Dict[str, Any]:
    """
    Retrieve the most relevant chunks for a query using hybrid
    (dense + BM25) search.

    Returns:
        {
            "query": "...",
            "results": [...],
            "context": "...",
            "controls_referenced": [...]   # de-duplicated control IDs
        }
    """

    results = hybrid_search(
        query=query,
        top_k=top_k,
        **filters,
    )

    context = build_context(results)

    controls_referenced = sorted(
        {
            control
            for result in results
            for control in (result.get("compliance_controls") or [])
        }
    )

    return {
        "query": query,
        "results": results,
        "context": context,
        "controls_referenced": controls_referenced,
    }


RAG_PROMPT_TEMPLATE = """
You are a cloud security expert.

Use ONLY the information contained in the context below.

If the answer is not present in the context, respond:

"I could not find this information in the provided documentation."

----------------------------
Relevant Compliance Controls
----------------------------

{controls}

----------------------------
Context
----------------------------

{context}

----------------------------
Question
----------------------------

{query}

----------------------------
Answer
----------------------------
"""


def build_rag_prompt(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    **filters,
) -> str:
    """
    Retrieve context and generate a ready-to-send RAG prompt.
    """

    data = retrieve_context(
        query=query,
        top_k=top_k,
        **filters,
    )

    controls = ", ".join(data["controls_referenced"]) or "None identified"

    return RAG_PROMPT_TEMPLATE.format(
        context=data["context"],
        query=query,
        controls=controls,
    )


def build_agent_working_memory(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    **filters,
) -> Dict[str, Any]:
    """
    Structured payload for Member 3's Security Analyst Agent, for
    when it wants raw structured data rather than a flattened prompt
    string (e.g. to reason over sources/controls programmatically
    before generating remediation).
    """

    data = retrieve_context(query=query, top_k=top_k, **filters)

    return {
        "query": query,
        "retrieved_chunks": [
            {
                "text": r.get("text"),
                "source_file": r.get("source_file"),
                "folder": r.get("folder"),
                "category": r.get("category"),
                "score": r.get("score"),
                "compliance_controls": r.get("compliance_controls", []),
                "compliance_frameworks": r.get("compliance_frameworks", []),
            }
            for r in data["results"]
        ],
        "compliance_controls_in_scope": data["controls_referenced"],
        "prompt": build_rag_prompt(query, top_k=top_k, **filters),
    }


if __name__ == "__main__":

    question = "Why is a public S3 bucket a security risk?"

    prompt = build_rag_prompt(
        query=question,
        top_k=DEFAULT_TOP_K,
    )

    print("\n========== GENERATED RAG PROMPT ==========\n")
    print(prompt)