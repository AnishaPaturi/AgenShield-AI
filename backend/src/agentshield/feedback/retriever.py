"""Deterministic, local retrieval of relevant historical feedback (Task 4.5).

The retriever finds stored :class:`FeedbackRecord` objects that are relevant to a
*new* finding.  It deliberately uses **no** embeddings, external APIs or vector
services and does not touch the existing AgentShield RAG system.

Scoring model (maximum 100 points)
----------------------------------
=====================  ======  ====================================================
Component              Points  Rule
=====================  ======  ====================================================
``finding_type``       40      Normalised finding types are exactly equal.
``iac_type``           25      Normalised IaC types are equal (aliases folded, e.g.
                               ``tf`` == ``hcl`` == ``terraform``).
``resource_type``      15      Normalised resource types are exactly equal.
``keywords``           0-20    ``20 * Jaccard`` similarity of the keyword sets built
                               from ``finding_type`` + ``vulnerability_context``.
=====================  ======  ====================================================

Keyword extraction lower-cases text, splits CamelCase / snake_case, drops common
stop-words and generic IaC words, folds simple plurals and removes the tokens of
the two resource types (resource similarity is already scored separately, so
``s3``/``bucket`` overlap must not make two *different* S3 problems look alike).

Relevance gate
--------------
Sharing only the IaC type and/or the resource type is **not** enough to be
relevant (an IAM wildcard policy and an S3 public-access finding are unrelated
even though both are Terraform).  A record is a candidate only if it has a
*vulnerability signal*:

* the finding types are equal, **or**
* the keyword sets share at least :data:`MIN_SHARED_KEYWORDS` keywords.

Candidates must additionally reach ``min_score`` (default
:data:`DEFAULT_MIN_SCORE`).

Ordering is fully deterministic: higher score first, then newer timestamp,
then ``feedback_id``.  The result never depends on insertion order.
"""

from __future__ import annotations

import re
from typing import FrozenSet, List, Optional, Set, Union

from .models import (
    FeedbackDecision,
    FeedbackQuery,
    FeedbackRecord,
    RetrievedFeedback,
)
from .store import FeedbackStore

# --------------------------------------------------------------------------- #
# Scoring configuration (documented above; deterministic)
# --------------------------------------------------------------------------- #
FINDING_TYPE_WEIGHT: float = 40.0
IAC_TYPE_WEIGHT: float = 25.0
RESOURCE_TYPE_WEIGHT: float = 15.0
KEYWORD_WEIGHT: float = 20.0
MAX_SCORE: float = (
    FINDING_TYPE_WEIGHT + IAC_TYPE_WEIGHT + RESOURCE_TYPE_WEIGHT + KEYWORD_WEIGHT
)

#: Minimum number of shared keywords that counts as a vulnerability signal when
#: the finding types are not equal.
MIN_SHARED_KEYWORDS: int = 2

#: Default minimum score for a record to be returned.
DEFAULT_MIN_SCORE: float = 20.0

_IAC_ALIASES = {
    "tf": "terraform",
    "hcl": "terraform",
    "terraform_hcl": "terraform",
    "cfn": "cloudformation",
    "aws_cloudformation": "cloudformation",
    "cloudformation_yaml": "cloudformation",
    "cloudformation_json": "cloudformation",
    "k8s": "kubernetes",
    "kubernetes_yaml": "kubernetes",
    "helm_values": "helm",
    "helm_chart": "helm",
}

_STOPWORDS: FrozenSet[str] = frozenset(
    {
        # English function words
        "a", "an", "and", "are", "as", "at", "be", "been", "by", "for", "from",
        "has", "have", "in", "is", "it", "its", "of", "on", "or", "that", "the",
        "this", "to", "was", "were", "will", "with", "can", "may", "should",
        "must", "do", "does", "into", "than", "then", "which", "when", "where",
        "if", "so",
        # Generic IaC words that carry no vulnerability meaning
        "aws", "terraform", "cloudformation", "kubernetes", "helm", "hcl",
        "yaml", "json", "resource", "resources", "configuration", "config",
        "template", "file", "iac", "tf", "cfn", "k8s",
    }
)

_CAMEL_1 = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
_CAMEL_2 = re.compile(r"(?<=[A-Z])(?=[A-Z][a-z])")
_NON_ALNUM = re.compile(r"[^a-z0-9]+")
_WORD = re.compile(r"[a-z0-9]+")


# --------------------------------------------------------------------------- #
# Text helpers
# --------------------------------------------------------------------------- #
def _split_camel(text: str) -> str:
    text = _CAMEL_1.sub(" ", text)
    return _CAMEL_2.sub(" ", text)


def normalize_key(value: Optional[str]) -> str:
    """Normalise an identifier: ``"S3PublicAccess"`` -> ``"s3_public_access"``."""
    if not value:
        return ""
    return _NON_ALNUM.sub("_", _split_camel(value).lower()).strip("_")


def normalize_iac_type(value: Optional[str]) -> str:
    """Normalise an IaC type and fold well-known aliases."""
    key = normalize_key(value)
    return _IAC_ALIASES.get(key, key)


def _fold_plural(token: str) -> str:
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 3 and token.endswith("s") and not token.endswith(("ss", "us")):
        return token[:-1]
    return token


def tokenize(text: Optional[str]) -> Set[str]:
    """Return the set of meaningful keywords contained in ``text``."""
    if not text:
        return set()
    words = _WORD.findall(_split_camel(text).lower())
    tokens = {_fold_plural(w) for w in words if w not in _STOPWORDS}
    return {t for t in tokens if len(t) >= 2 and t not in _STOPWORDS}


def _jaccard(a: Set[str], b: Set[str]) -> float:
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


# --------------------------------------------------------------------------- #
# Scoring
# --------------------------------------------------------------------------- #
def score_feedback(
    query: FeedbackQuery, record: FeedbackRecord
) -> Optional[RetrievedFeedback]:
    """Score ``record`` against ``query``.

    Returns ``None`` when the record has no vulnerability signal (i.e. it is
    not relevant), otherwise a :class:`RetrievedFeedback` with the total score,
    the per-component breakdown and the list of matched components.
    """
    finding_match = (
        normalize_key(query.finding_type) != ""
        and normalize_key(query.finding_type) == normalize_key(record.finding_type)
    )
    iac_match = (
        normalize_iac_type(query.iac_type) != ""
        and normalize_iac_type(query.iac_type) == normalize_iac_type(record.iac_type)
    )
    q_resource = normalize_key(query.resource_type)
    r_resource = normalize_key(record.resource_type)
    resource_match = q_resource != "" and q_resource == r_resource

    # Keyword sets: resource-type tokens are excluded (scored separately).
    resource_tokens = tokenize(query.resource_type) | tokenize(record.resource_type)
    q_keywords = (
        tokenize(query.finding_type) | tokenize(query.vulnerability_context)
    ) - resource_tokens
    r_keywords = (
        tokenize(record.finding_type) | tokenize(record.vulnerability_context)
    ) - resource_tokens
    shared = q_keywords & r_keywords

    has_signal = finding_match or len(shared) >= MIN_SHARED_KEYWORDS
    if not has_signal:
        return None

    breakdown = {
        "finding_type": FINDING_TYPE_WEIGHT if finding_match else 0.0,
        "iac_type": IAC_TYPE_WEIGHT if iac_match else 0.0,
        "resource_type": RESOURCE_TYPE_WEIGHT if resource_match else 0.0,
        "keywords": round(KEYWORD_WEIGHT * _jaccard(q_keywords, r_keywords), 4),
    }
    matched_on: List[str] = [name for name, pts in breakdown.items() if pts > 0]
    total = round(sum(breakdown.values()), 4)
    return RetrievedFeedback(
        record=record,
        score=total,
        matched_on=matched_on,
        score_breakdown=breakdown,
    )


# --------------------------------------------------------------------------- #
# Retriever
# --------------------------------------------------------------------------- #
class FeedbackRetriever:
    """Find historical feedback relevant to a new finding."""

    def __init__(
        self, store: FeedbackStore, min_score: float = DEFAULT_MIN_SCORE
    ) -> None:
        self._store = store
        self._min_score = float(min_score)

    @property
    def min_score(self) -> float:
        return self._min_score

    def retrieve(
        self,
        query: FeedbackQuery,
        *,
        top_k: Optional[int] = 5,
        decision: Optional[Union[FeedbackDecision, str]] = None,
        min_score: Optional[float] = None,
    ) -> List[RetrievedFeedback]:
        """Return relevant feedback for ``query``, best match first.

        Args:
            query: The new finding.
            top_k: Maximum number of results. ``None`` returns *all* relevant
                feedback; ``0`` returns an empty list.
            decision: If given, only return ACCEPTED or only REJECTED feedback.
            min_score: Override the retriever's minimum score.
        """
        if top_k is not None and top_k < 0:
            raise ValueError("top_k must be >= 0 or None")
        wanted = _coerce_decision(decision)
        threshold = self._min_score if min_score is None else float(min_score)

        results: List[RetrievedFeedback] = []
        for record in self._store.get_all_feedback():
            if wanted is not None and record.decision != wanted:
                continue
            scored = score_feedback(query, record)
            if scored is None or scored.score < threshold:
                continue
            results.append(scored)

        results.sort(
            key=lambda r: (-r.score, -r.record.timestamp.timestamp(), r.record.feedback_id)
        )
        if top_k is not None:
            results = results[:top_k]
        return results

    def retrieve_similar_feedback(
        self,
        finding_type: str,
        iac_type: str,
        resource_type: Optional[str] = None,
        vulnerability_context: Optional[str] = None,
        *,
        top_k: Optional[int] = 5,
        decision: Optional[Union[FeedbackDecision, str]] = None,
        min_score: Optional[float] = None,
    ) -> List[RetrievedFeedback]:
        """Keyword-argument flavour of :meth:`retrieve`."""
        query = FeedbackQuery(
            finding_type=finding_type,
            iac_type=iac_type,
            resource_type=resource_type,
            vulnerability_context=vulnerability_context,
        )
        return self.retrieve(query, top_k=top_k, decision=decision, min_score=min_score)

    def retrieve_accepted(
        self, query: FeedbackQuery, *, top_k: Optional[int] = 5,
        min_score: Optional[float] = None,
    ) -> List[RetrievedFeedback]:
        """Only previously ACCEPTED patches (positive examples)."""
        return self.retrieve(
            query, top_k=top_k, decision=FeedbackDecision.ACCEPTED, min_score=min_score
        )

    def retrieve_rejected(
        self, query: FeedbackQuery, *, top_k: Optional[int] = 5,
        min_score: Optional[float] = None,
    ) -> List[RetrievedFeedback]:
        """Only previously REJECTED patches (negative examples)."""
        return self.retrieve(
            query, top_k=top_k, decision=FeedbackDecision.REJECTED, min_score=min_score
        )


def _coerce_decision(
    decision: Optional[Union[FeedbackDecision, str]]
) -> Optional[FeedbackDecision]:
    if decision is None:
        return None
    if isinstance(decision, FeedbackDecision):
        return decision
    try:
        return FeedbackDecision(str(decision).strip().upper())
    except ValueError as exc:
        raise ValueError(
            f"decision must be ACCEPTED, REJECTED or None (got {decision!r})"
        ) from exc
