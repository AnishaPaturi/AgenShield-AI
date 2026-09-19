"""Evaluation metrics calculator for IaC security benchmarks (Task 5.3)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BenchmarkMetrics:
    total_cases: int = 0
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    true_negatives: int = 0
    patches_generated: int = 0
    patches_validated: int = 0
    latencies_ms: list[float] = None

    def __post_init__(self) -> None:
        if self.latencies_ms is None:
            self.latencies_ms = []

    @property
    def precision(self) -> float:
        denom = self.true_positives + self.false_positives
        return round(self.true_positives / denom, 4) if denom > 0 else 1.0

    @property
    def recall(self) -> float:
        denom = self.true_positives + self.false_negatives
        return round(self.true_positives / denom, 4) if denom > 0 else 1.0

    @property
    def f1_score(self) -> float:
        p, r = self.precision, self.recall
        return round(2 * (p * r) / (p + r), 4) if (p + r) > 0 else 0.0

    @property
    def hallucination_rate(self) -> float:
        denom = self.true_positives + self.false_positives
        return round(self.false_positives / denom, 4) if denom > 0 else 0.0

    @property
    def patch_pass_rate(self) -> float:
        return (
            round(self.patches_validated / self.patches_generated, 4)
            if self.patches_generated > 0
            else 1.0
        )

    @property
    def mean_latency_ms(self) -> float:
        return (
            round(sum(self.latencies_ms) / len(self.latencies_ms), 1)
            if self.latencies_ms
            else 0.0
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_cases": self.total_cases,
            "true_positives": self.true_positives,
            "false_positives": self.false_positives,
            "false_negatives": self.false_negatives,
            "true_negatives": self.true_negatives,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "hallucination_rate": self.hallucination_rate,
            "patch_pass_rate": self.patch_pass_rate,
            "mean_latency_ms": self.mean_latency_ms,
        }
