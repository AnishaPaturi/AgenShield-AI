"""
cache.py
--------

Maintains a cache of processed documents using file hashes.

Purpose:
    Prevent unchanged PDFs from being processed again.

Workflow:
    PDF
      ↓
    Compute MD5 Hash
      ↓
    Compare with kb_cache.json
      ↓
    Changed?
        YES → Process
        NO  → Skip
"""

import hashlib
import json
from pathlib import Path
from typing import Dict

PROJECT_ROOT = Path(__file__).resolve().parents[4]

CACHE_FILE = PROJECT_ROOT / "kb_cache.json"


def compute_hash(file_path: Path) -> str:
    """
    Compute MD5 hash of a file.
    """

    md5 = hashlib.md5()

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(8192)

            if not chunk:
                break

            md5.update(chunk)

    return md5.hexdigest()


def load_cache() -> Dict[str, str]:
    """
    Load cache from disk.
    """

    if not CACHE_FILE.exists():
        return {}

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cache(cache: Dict[str, str]):
    """
    Save cache back to disk.
    """

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=4)


def file_changed(file_path: Path) -> bool:
    """
    Returns True if file is new or modified.
    """

    cache = load_cache()

    current_hash = compute_hash(file_path)

    old_hash = cache.get(str(file_path))

    return current_hash != old_hash


def update_cache(file_path: Path):
    """
    Store the latest hash of a processed file.
    """

    cache = load_cache()

    cache[str(file_path)] = compute_hash(file_path)

    save_cache(cache)


def clear_cache():
    """
    Clears the cache file.
    """

    save_cache({})


if __name__ == "__main__":

    print("Knowledge Base Cache")

    print("Cache file:", CACHE_FILE)

    cache = load_cache()

    print(f"Cached Files: {len(cache)}")

    for file_name in cache:
        print(file_name)