"""
chunker.py
----------
STEP 3 of the RAG pipeline: Text Chunking.

Purpose:
    Split loaded PDF pages into smaller semantic chunks before
    generating embeddings, and annotate each chunk with the
    regulatory compliance controls it touches on (Task 2.3).

Why chunking is necessary:
    - Embedding models have input size limits.
    - Large documents produce poor-quality embeddings.
    - Small, focused chunks improve retrieval accuracy.

Defaults (config.py):
    Chunk Size:    500 characters
    Chunk Overlap: 50 characters

This overlap preserves context across chunk boundaries.
"""

import hashlib
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .compliance import annotate_chunk_metadata
from .config import CHUNK_OVERLAP, CHUNK_SIZE


def _stable_chunk_id(source_file: str, text: str) -> str:
    """
    Deterministic chunk ID based on source file + content hash,
    rather than a positional index. This means re-running the
    pipeline on an unchanged document yields the *same* chunk IDs,
    which matters once we start doing semantic dedup and incremental
    upserts keyed by ID.
    """

    digest = hashlib.md5(text.encode("utf-8")).hexdigest()[:10]

    return f"{source_file}_{digest}"


def chunk_documents(
    documents: List[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
    tag_compliance: bool = True,
) -> List[Document]:
    """
    Split page-level LangChain Documents into smaller semantic chunks.

    Args:
        documents: List of page-level LangChain Documents.
        chunk_size: Maximum number of characters per chunk.
        chunk_overlap: Number of overlapping characters between chunks.
        tag_compliance: If True, annotate each chunk with matching
            compliance control IDs / frameworks.

    Returns:
        List[Document]: Chunked documents with preserved metadata.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
        length_function=len,
    )

    chunks = splitter.split_documents(documents)

    for chunk in chunks:

        source_file = chunk.metadata.get("source_file", "document")

        chunk.metadata["chunk_id"] = _stable_chunk_id(source_file, chunk.page_content)

        if tag_compliance:
            chunk.metadata.update(annotate_chunk_metadata(chunk.page_content))

    print(
        f"[chunker] {len(documents)} pages -> "
        f"{len(chunks)} chunks "
        f"(chunk_size={chunk_size}, "
        f"chunk_overlap={chunk_overlap}, "
        f"compliance_tagged={tag_compliance})"
    )

    return chunks


if __name__ == "__main__":

    from .loaders import load_all_documents

    documents = load_all_documents()
    chunks = chunk_documents(documents)

    if chunks:
        print("\n========== SAMPLE CHUNK ==========\n")
        print(chunks[0].page_content)
        print("\nMetadata:")
        print(chunks[0].metadata)