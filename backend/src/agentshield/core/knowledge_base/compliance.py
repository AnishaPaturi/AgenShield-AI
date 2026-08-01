"""
compliance.py
-------------
STEP: Regulatory Compliance Mapping (Task 2.3).

Purpose:
    Crosswalk security documentation chunks against SOC 2, HIPAA,
    PCI-DSS, and NIST 800-53 control IDs so that retrieved context
    can be traced back to a specific compliance requirement, e.g.
    NIST-AC-6, PCI-DSS-1.3.

Workflow:
    Document Chunk
          ↓
    Load Compliance Mapping
          ↓
    Keyword Matching
          ↓
    Match Controls
          ↓
    Match Frameworks
          ↓
    Annotate Chunk Metadata
"""

import json
from functools import lru_cache
from typing import Dict, List

from .config import COMPLIANCE_MAP_FILE


@lru_cache(maxsize=1)
def load_control_map() -> Dict[str, Dict[str, List[str]]]:
    """
    Load the framework -> control_id -> keywords mapping.

    Cached so the JSON file is parsed only once per process.
    """

    if not COMPLIANCE_MAP_FILE.exists():
        raise FileNotFoundError(
            f"Compliance mapping file not found: "
            f"{COMPLIANCE_MAP_FILE}"
        )

    with open(
        COMPLIANCE_MAP_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


def match_controls(text: str) -> List[str]:
    """
    Return every compliance control whose keywords appear in
    the supplied text.

    Example:
        Input:
            "Public S3 bucket with no encryption."

        Output:
            ["PCI-DSS-3.4", "NIST-AC-6"]
    """

    text_lower = text.lower()

    control_map = load_control_map()

    matched: List[str] = []

    for _, controls in control_map.items():

        for control_id, keywords in controls.items():

            if any(
                keyword.lower() in text_lower
                for keyword in keywords
            ):

                matched.append(control_id)

    return sorted(set(matched))


def match_frameworks(text: str) -> List[str]:
    """
    Return every framework that has at least one matching
    control in the supplied text.
    """

    text_lower = text.lower()

    control_map = load_control_map()

    matched: List[str] = []

    for framework, controls in control_map.items():

        for keywords in controls.values():

            if any(
                keyword.lower() in text_lower
                for keyword in keywords
            ):

                matched.append(framework)

                break

    return sorted(set(matched))


def annotate_chunk_metadata(
    text: str,
) -> Dict[str, List[str]]:
    """
    Build metadata that is attached to each chunk before it
    is stored inside Qdrant.

    Returns:
        {
            "compliance_controls": [...],
            "compliance_frameworks": [...]
        }
    """

    return {
        "compliance_controls": match_controls(text),
        "compliance_frameworks": match_frameworks(text),
    }


if __name__ == "__main__":

    sample = (
        "The S3 bucket policy grants public read access "
        "without encryption and audit logging."
    )

    print("\n========== COMPLIANCE TEST ==========\n")

    print("Sample Text:\n")
    print(sample)

    print("\nMatched Controls:\n")
    print(match_controls(sample))

    print("\nMatched Frameworks:\n")
    print(match_frameworks(sample))

    print("\nMetadata:\n")
    print(annotate_chunk_metadata(sample))