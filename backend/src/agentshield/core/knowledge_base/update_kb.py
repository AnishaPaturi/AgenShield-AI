"""
update_kb.py
------------

STEP 9 of the RAG pipeline: Incremental Knowledge Base Updates.

Purpose:
    Update the Knowledge Base by processing only newly added or
    modified PDF documents and scraped content, then keep the BM25
    sparse index synchronized with Qdrant.

Workflow:

        Scan data/ + data_scraped/
                ↓
        Compare File Hash
                ↓
        New / Modified ?
          │          │
         Yes        No
          │          │
          ▼          ▼
      Load File     Skip
          │
          ▼
      Chunk Documents
          │
          ▼
    Compliance Annotation
          │
          ▼
    Semantic Deduplication
          │
          ▼
      Generate Embeddings
          │
          ▼
      Upsert to Qdrant
          │
          ▼
      Update Cache
          │
          ▼
      Rebuild BM25 Index

Advantages:
    • Incremental updates only.
    • Avoids rebuilding the entire KB.
    • Keeps dense and sparse retrieval synchronized.
"""

from pathlib import Path

from .cache import file_changed, update_cache
from .chunker import chunk_documents
from .config import DATA_ROOT, SCRAPED_ROOT
from .hybrid_search import build_bm25_index
from .loaders import load_single_pdf, load_single_text
from .vector_db import (
    create_collection,
    get_client,
    upsert_chunks,
)


def incremental_update(
    data_root: Path = DATA_ROOT,
    scraped_root: Path = SCRAPED_ROOT,
) -> None:
    """
    Process only new or modified documents and update the
    Knowledge Base incrementally.
    """

    client = get_client()

    try:

        create_collection(client)

        documents = []

        # ============================================================
        # Process PDF Documentation
        # ============================================================

        if data_root.exists():

            for folder in sorted(data_root.iterdir()):

                if not folder.is_dir():
                    continue

                for pdf_path in folder.rglob("*.pdf"):

                    if file_changed(pdf_path):

                        print(
                            f"[update_kb] Processing PDF: "
                            f"{pdf_path.name}"
                        )

                        try:

                            documents.extend(
                                load_single_pdf(
                                    pdf_path,
                                    folder.name,
                                )
                            )

                            update_cache(pdf_path)

                        except Exception as e:

                            print(
                                f"[update_kb] Failed to process "
                                f"{pdf_path.name}: {e}"
                            )

                    else:

                        print(
                            f"[update_kb] Skipping PDF: "
                            f"{pdf_path.name}"
                        )

        # ============================================================
        # Process Scraped Content
        # ============================================================

        if scraped_root.exists():

            for folder in sorted(scraped_root.iterdir()):

                if not folder.is_dir():
                    continue

                for file_path in folder.rglob("*"):

                    if not file_path.is_file():
                        continue

                    if file_path.suffix.lower() not in (
                        ".txt",
                        ".json",
                        ".md",
                    ):
                        continue

                    if file_changed(file_path):

                        print(
                            f"[update_kb] Processing Scraped File: "
                            f"{file_path.name}"
                        )

                        try:

                            documents.extend(
                                load_single_text(
                                    file_path,
                                    folder.name,
                                )
                            )

                            update_cache(file_path)

                        except Exception as e:

                            print(
                                f"[update_kb] Failed to process "
                                f"{file_path.name}: {e}"
                            )

                    else:

                        print(
                            f"[update_kb] Skipping Scraped File: "
                            f"{file_path.name}"
                        )

        # ============================================================
        # Nothing Changed
        # ============================================================

        if not documents:

            print(
                "\n[update_kb] Knowledge Base already up-to-date."
            )

            return

        # ============================================================
        # Chunk Documents
        # ============================================================

        print("\n[update_kb] Chunking documents...")

        chunks = chunk_documents(documents)

        # ============================================================
        # Update Vector Database
        # ============================================================

        print(
            "[update_kb] Updating Vector Database..."
        )

        upsert_chunks(
            client=client,
            chunks=chunks,
        )

        # ============================================================
        # Rebuild BM25 Index
        # ============================================================

        print(
            "[update_kb] Rebuilding BM25 Index..."
        )

        build_bm25_index(client)

        print(
            f"\n[update_kb] Successfully indexed "
            f"{len(chunks)} chunks."
        )

    finally:

        client.close()


if __name__ == "__main__":

    incremental_update()