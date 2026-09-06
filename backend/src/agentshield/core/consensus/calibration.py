"""Confidence calibration and reliability metrics (Task 3.2).

A raw ensemble score is only a *calibrated* confidence if it matches the
empirical frequency of correctness: of the findings scored 0.90, roughly 90%
should be true positives. This module supplies

* :class:`ConfidenceCalibrator` -- monotonic Platt/temperature scaling in
  logit space, fitted from labelled triage outcomes.
* Reliability metrics -- Expected Calibration Error and Brier score -- so the
  calibration claim can be measured rather than asserted.

Implemented in pure Python: the calibrator is fitted from a handful of
labelled outcomes and must stay dependency-free and deterministic.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

# Clamp probabilities away from 0/1 so the logit stays finite.
_EPS: float = 1e-6

# Smallest slope a fitted calibrator may take. A slope of 0 maps every input to
# the same output, which would erase the ranking between findings.
MIN_SLOPE: float = 0.05

# Light L2 pull of the slope toward 1.0, so a small or low-variance sample
# cannot produce an extreme rescaling.
SLOPE_RIDGE: float = 0.01


def _clamp(value: float, low: float = _EPS, high: float = 1.0 - _EPS) -> float:
    return min(high, max(low, value))


def _logit(probability: float) -> float:
    p = _clamp(probability)
    return math.log(p / (1.0 - p))


def _sigmoid(value: float) -> float:
    # Branch on sign to avoid overflow in exp for large magnitudes.
    if value >= 0.0:
        return 1.0 / (1.0 + math.exp(-value))
    exp_v = math.exp(value)
    return exp_v / (1.0 + exp_v)


@dataclass
class ReliabilityBin:
    """One bucket of a reliability diagram."""

    lower: float
    upper: float
    count: int
    mean_confidence: float
    empirical_accuracy: float

    @property
    def gap(self) -> float:
        """Signed calibration gap; positive means over-confident."""
        return self.mean_confidence - self.empirical_accuracy


@dataclass
class CalibrationReport:
    """Measured calibration quality of a set of confidence scores."""

    expected_calibration_error: float
    brier_score: float
    sample_count: int
    bins: list[ReliabilityBin] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        """Serializable view for reports and dashboards."""
        return {
            "expected_calibration_error": self.expected_calibration_error,
            "brier_score": self.brier_score,
            "sample_count": self.sample_count,
            "bins": [
                {
                    "range": [round(b.lower, 4), round(b.upper, 4)],
                    "count": b.count,
                    "mean_confidence": round(b.mean_confidence, 4),
                    "empirical_accuracy": round(b.empirical_accuracy, 4),
                    "gap": round(b.gap, 4),
                }
                for b in self.bins
            ],
        }


def reliability_bins(
    scores: list[float], outcomes: list[int], n_bins: int = 10
) -> list[ReliabilityBin]:
    """Bucket score/outcome pairs into equal-width reliability bins."""
    if len(scores) != len(outcomes):
        raise ValueError("scores and outcomes must have equal length")

    bins: list[ReliabilityBin] = []
    width = 1.0 / n_bins

    for i in range(n_bins):
        lower = i * width
        upper = (i + 1) * width
        # Last bin is closed on the right so a score of exactly 1.0 lands.
        members = [
            (s, o)
            for s, o in zip(scores, outcomes, strict=True)
            if (lower <= s < upper) or (i == n_bins - 1 and s == upper)
        ]
        if not members:
            continue
        mean_conf = sum(s for s, _ in members) / len(members)
        accuracy = sum(o for _, o in members) / len(members)
        bins.append(
            ReliabilityBin(
                lower=lower,
                upper=upper,
                count=len(members),
                mean_confidence=mean_conf,
                empirical_accuracy=accuracy,
            )
        )

    return bins


def expected_calibration_error(
    scores: list[float], outcomes: list[int], n_bins: int = 10
) -> float:
    """Weighted mean absolute gap between confidence and accuracy.

        ECE = sum_b (n_b / N) * |acc(b) - conf(b)|

    0.0 is perfect calibration; 1.0 is maximally miscalibrated.
    """
    if not scores:
        return 0.0
    total = len(scores)
    bins = reliability_bins(scores, outcomes, n_bins=n_bins)
    return round(sum((b.count / total) * abs(b.gap) for b in bins), 6)


def brier_score(scores: list[float], outcomes: list[int]) -> float:
    """Mean squared error between confidence and binary outcome."""
    if not scores:
        return 0.0
    if len(scores) != len(outcomes):
        raise ValueError("scores and outcomes must have equal length")
    return round(
        sum((s - o) ** 2 for s, o in zip(scores, outcomes, strict=True)) / len(scores), 6
    )


@dataclass
class ConfidenceCalibrator:
    """Monotonic confidence calibration via Platt scaling in logit space.

        C_calibrated = sigmoid(a * logit(C_raw) + b)

    The identity calibrator (a = 1.0, b = 0.0) is the default and passes
    scores through untouched, so an unfitted pipeline behaves exactly like the
    raw ensemble formula. A slope below 1.0 shrinks scores toward 0.5,
    correcting the over-confidence LLMs typically exhibit.
    """

    a: float = 1.0
    b: float = 0.0
    fitted: bool = False
    sample_count: int = 0

    @property
    def is_identity(self) -> bool:
        """True when this calibrator leaves scores unchanged."""
        return self.a == 1.0 and self.b == 0.0

    @property
    def temperature(self) -> float:
        """Equivalent temperature T = 1 / a; above 1.0 means scores soften."""
        return float("inf") if self.a == 0.0 else 1.0 / self.a

    def apply(self, score: float) -> float:
        """Map a raw confidence score onto the calibrated scale."""
        if self.is_identity:
            # Exact pass-through: avoids float drift through logit/sigmoid.
            return round(min(1.0, max(0.0, score)), 4)
        calibrated = _sigmoid(self.a * _logit(score) + self.b)
        return round(min(1.0, max(0.0, calibrated)), 4)

    def apply_all(self, scores: list[float]) -> list[float]:
        """Vectorized :meth:`apply`."""
        return [self.apply(s) for s in scores]

    def fit(
        self,
        scores: list[float],
        outcomes: list[int],
        learning_rate: float = 0.5,
        iterations: int = 2000,
        min_slope: float = MIN_SLOPE,
        ridge: float = SLOPE_RIDGE,
    ) -> ConfidenceCalibrator:
        """Fit the slope and intercept by minimizing negative log-likelihood.

        ``outcomes`` are ground-truth labels from human triage: 1 when the
        finding was confirmed a true positive, 0 when rejected. Gradient
        descent is used rather than a solver dependency; the objective is
        convex in the two parameters so a fixed schedule converges reliably.

        Two guards keep the fitted map usable as a *ranking* function, not just
        a probability estimate:

        * ``min_slope`` is enforced on every step, not merely at the end. Fit
          data with little spread in raw scores (for example a batch where
          every finding was reported at 0.95) leaves the slope unidentifiable:
          the gradient drives it negative or to zero, collapsing the
          calibrator into a constant that maps every finding to one value and
          destroys the ordering the audit queue prioritizes by. Clamping
          inside the loop lets the intercept absorb the remaining error
          instead.
        * ``ridge`` lightly pulls the slope back toward 1.0, so a small or
          degenerate sample cannot produce an extreme rescaling.
        """
        if len(scores) != len(outcomes):
            raise ValueError("scores and outcomes must have equal length")
        if not scores:
            return self

        logits = [_logit(s) for s in scores]
        n = float(len(scores))
        a, b = 1.0, 0.0

        for _ in range(iterations):
            grad_a = 0.0
            grad_b = 0.0
            for z, y in zip(logits, outcomes, strict=True):
                p = _sigmoid(a * z + b)
                residual = p - y
                grad_a += residual * z
                grad_b += residual
            a -= learning_rate * ((grad_a / n) + 2.0 * ridge * (a - 1.0))
            b -= learning_rate * (grad_b / n)
            # Keep the mapping strictly increasing throughout the descent.
            a = max(min_slope, a)

        self.a = a
        self.b = b
        self.fitted = True
        self.sample_count = len(scores)
        return self

    def evaluate(
        self, scores: list[float], outcomes: list[int], n_bins: int = 10
    ) -> CalibrationReport:
        """Measure calibration quality of the calibrated output."""
        calibrated = self.apply_all(scores)
        return CalibrationReport(
            expected_calibration_error=expected_calibration_error(
                calibrated, outcomes, n_bins=n_bins
            ),
            brier_score=brier_score(calibrated, outcomes),
            sample_count=len(scores),
            bins=reliability_bins(calibrated, outcomes, n_bins=n_bins),
        )
