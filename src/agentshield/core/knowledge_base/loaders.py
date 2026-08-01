"""
loaders.py
----------
STEP 2 of the RAG pipeline: Document Loading.

Purpose:
    Walk the entire data/ directory (aws/, azure/, gcp/, terraform/,
    kubernetes/, nist/, cis/, owasp/, mitre/) and load every PDF into
    LangChain "Document" objects, tagging each one with metadata that
    tells us WHERE it came from (cloud provider, category, filename).

    Also loads raw text/HTML dumps produced by the continuous
    scraper (scrapers.py) from data_scraped/, so freshly-pulled NVD/
    CVE and best-practice content flows through the same chunk ->
    embed -> upsert path as PDFs.

Why metadata matters:
    When Member 3's LLM later asks "how do I secure an S3 bucket",
    we don't just want ANY chunk back — we want chunks that are
    actually from AWS documentation, not Azure. Metadata lets us
    filter search results by source, which massively increases
    precision.
"""

from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from .config import CATEGORY_MAP, DATA_ROOT, SCRAPED_ROOT

# Folder -> metadata category mapping now lives in config.yaml's
# `categories:` block (see config.py). Add a new source there, not here.


def load_single_pdf(file_path: Path, source_folder: str) -> List[Document]:
    """
    Load a single PDF and return a list of LangChain Document objects.

    PyPDFLoader returns one Document per page.
    Metadata is attached to every page so it remains available
    throughout chunking, embedding, storage and retrieval.
    """

    loader = PyPDFLoader(str(file_path))
    pages = loader.load()

    for page in pages:
        page.metadata.update(
            {
                "source_file": file_path.name,
                "folder": source_folder,
                "category": CATEGORY_MAP.get(source_folder, "general"),
                "full_path": str(file_path),
            }
        )

    return pages


def load_single_text(file_path: Path, source_folder: str) -> List[Document]:
    """
    Load a single .txt/.json/.md file produced by the scraper (e.g. an
    NVD CVE record or a scraped best-practices page saved as plain
    text) and wrap it as a single-page Document, tagged the same way
    a PDF page would be.
    """

    text = file_path.read_text(encoding="utf-8", errors="ignore")

    return [
        Document(
            page_content=text,
            metadata={
                "source_file": file_path.name,
                "folder": source_folder,
                "category": CATEGORY_MAP.get(source_folder, "general"),
                "full_path": str(file_path),
            },
        )
    ]


def load_all_documents(data_root: Path = DATA_ROOT) -> List[Document]:
    """
    Load every PDF under the project's data/ directory.

    Returns:
        List[Document]:
            One Document object per PDF page.
    """

    all_documents: List[Document] = []

    if not data_root.exists():
        raise FileNotFoundError(
            f"'{data_root}' not found.\n"
            "Expected structure:\n"
            "data/aws/*.pdf\n"
            "data/azure/*.pdf\n"
            "data/gcp/*.pdf\n"
            "..."
        )

    for subfolder in sorted(data_root.iterdir()):

        if not subfolder.is_dir():
            continue

        pdf_files = list(subfolder.rglob("*.pdf"))

        print(
            f"[loaders] Found {len(pdf_files)} PDF(s) "
            f"in '{subfolder.name}/'"
        )

        for pdf in pdf_files:

            try:
                docs = load_single_pdf(
                    pdf,
                    source_folder=subfolder.name,
                )

                all_documents.extend(docs)

            except Exception as e:
                print(f"[loaders] Failed to load {pdf}: {e}")

    print(
        f"\n[loaders] Total pages loaded: {len(all_documents)}"
    )

    return all_documents


def load_all_scraped(scraped_root: Path = SCRAPED_ROOT) -> List[Document]:
    """
    Load every text/json/markdown file under data_scraped/, mirroring
    load_all_documents() but for continuously-scraped content instead
    of static PDFs.
    """

    all_documents: List[Document] = []

    if not scraped_root.exists():
        print(f"[loaders] '{scraped_root}' not found, nothing to load.")
        return all_documents

    for subfolder in sorted(scraped_root.iterdir()):

        if not subfolder.is_dir():
            continue

        text_files = [
            f for f in subfolder.rglob("*")
            if f.is_file() and f.suffix.lower() in (".txt", ".json", ".md")
        ]

        print(f"[loaders] Found {len(text_files)} scraped file(s) in '{subfolder.name}/'")

        for text_file in text_files:

            try:
                all_documents.extend(load_single_text(text_file, subfolder.name))

            except Exception as e:
                print(f"[loaders] Failed to load {text_file}: {e}")

    print(f"[loaders] Total scraped documents loaded: {len(all_documents)}")

    return all_documents


if __name__ == "__main__":

    documents = load_all_documents()

    if documents:
        print("\n========== SAMPLE DOCUMENT ==========\n")
        print(documents[0].page_content[:300])
        print("\nMetadata:")
        print(documents[0].metadata)