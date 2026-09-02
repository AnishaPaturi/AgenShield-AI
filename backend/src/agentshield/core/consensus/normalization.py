"""Normalization primitives for cross-model consensus (Task 3.2).

Different LLMs describe the *same* vulnerability with different rule IDs,
titles, and phrasing. These helpers project heterogeneous model output onto a
canonical space so that agreement can be measured mathematically rather than
by exact string equality.
"""

from __future__ import annotations

import re

from agentshield.core.schemas.vulnerability import Severity

# Ordinal ranks used for severity distance computations.
SEVERITY_RANK: dict[Severity, int] = {
    Severity.INFORMATIONAL: 0,
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}

MAX_SEVERITY_DISTANCE: int = 4

# Vendor/tool prefixes stripped when deriving a rule family. Ordered longest
# first so that e.g. "CKV2" is matched before "CKV".
_RULE_PREFIXES: tuple[str, ...] = (
    "CKV2",
    "CKV",
    "ASDEF",
    "ASAWS",
    "ASAZURE",
    "ASGCP",
    "ASK8S",
    "ASINFO",
    "AS",
)

# Domain stopwords: extremely common in security prose and therefore carry no
# discriminative signal when comparing two findings.
_STOPWORDS: frozenset[str] = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "by", "can", "could", "for",
        "from", "has", "have", "in", "is", "it", "its", "may", "not", "of",
        "on", "or", "should", "that", "the", "this", "to", "which", "with",
        # security-domain filler
        "aws", "azure", "gcp", "cloud", "configuration", "configured",
        "detected", "finding", "issue", "resource", "risk", "security",
        "vulnerability",
    }
)


def normalize_resource(resource: str) -> str:
    """Canonicalize an affected-resource identifier.

    Collapses the many spellings models use for one resource, e.g.
    ``resource.aws_s3_bucket.data_bucket``, ``"aws_s3_bucket.data_bucket"``
    and ``aws_s3_bucket/data_bucket`` all normalize to
    ``aws_s3_bucket.data_bucket``.
    """
    text = resource.strip().strip("\"'").lower()
    text = re.sub(r"^(resource|data|module)\.", "", text)
    parts = [p for p in re.split(r"[./]", text) if p]
    if not parts:
        return ""
    # Keep the trailing ``<type>.<name>`` pair; drop provider/module prefixes.
    return ".".join(parts[-2:])


def normalize_rule_id(rule_id: str) -> str:
    """Reduce a rule identifier to its vendor-independent family."""
    text = re.sub(r"[^A-Z0-9]", "", rule_id.strip().upper())
    for prefix in _RULE_PREFIXES:
        if text.startswith(prefix) and len(text) > len(prefix):
            return text[len(prefix) :]
    return text


def tokenize(text: str) -> set[str]:
    """Split prose into a discriminative lowercase token set."""
    words = re.findall(r"[a-z0-9_]+", text.lower())
    return {w for w in words if len(w) > 2 and w not in _STOPWORDS}


def jaccard(left: set[str], right: set[str]) -> float:
    """Jaccard index of two sets; 1.0 when both are empty."""
    if not left and not right:
        return 1.0
    union = left | right
    if not union:
        return 1.0
    return len(left & right) / len(union)


def text_similarity(left: str, right: str) -> float:
    """Token-set similarity between two natural-language descriptions."""
    return jaccard(tokenize(left), tokenize(right))


def severity_distance(left: Severity, right: Severity) -> int:
    """Absolute ordinal distance between two severity levels (0..4)."""
    return abs(SEVERITY_RANK.get(left, 0) - SEVERITY_RANK.get(right, 0))


def interval_jaccard(
    left: tuple[int, int], right: tuple[int, int]
) -> float:
    """Jaccard overlap of two inclusive ``(start, end)`` line intervals."""
    l_start, l_end = min(left), max(left)
    r_start, r_end = min(right), max(right)

    intersection = max(0, min(l_end, r_end) - max(l_start, r_start) + 1)
    union = max(l_end, r_end) - min(l_start, r_start) + 1
    if union <= 0:
        return 1.0
    return intersection / union
