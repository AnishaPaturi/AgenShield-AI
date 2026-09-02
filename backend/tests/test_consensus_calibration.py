"""Tests for confidence calibration and reliability metrics (Task 3.2)."""

import pytest

from agentshield.core.consensus import (
    ConfidenceCalibrator,
    brier_score,
    expected_calibration_error,
    reliability_bins,
)

# --------------------------------------------------------------------------
# Reliability metrics
# --------------------------------------------------------------------------


def test_perfectly_calibrated_scores_have_zero_ece():
    # Every score is 0.0 or 1.0 and always correct.
    scores = [1.0, 1.0, 0.0, 0.0]
    outcomes = [1, 1, 0, 0]
    assert expected_calibration_error(scores, outcomes) == 0.0
    assert brier_score(scores, outcomes) == 0.0


def test_maximally_overconfident_scores_have_ece_near_one():
    scores = [1.0, 1.0, 1.0, 1.0]
    outcomes = [0, 0, 0, 0]
    assert expected_calibration_error(scores, outcomes) == pytest.approx(1.0)
    assert brier_score(scores, outcomes) == pytest.approx(1.0)


def test_ece_measures_the_gap_between_confidence_and_accuracy():
    # Ten findings all scored 0.90, but only half were true positives.
    scores = [0.90] * 10
    outcomes = [1] * 5 + [0] * 5
    # |0.90 - 0.50| = 0.40
    assert expected_calibration_error(scores, outcomes) == pytest.approx(0.40)


def test_ece_and_brier_on_empty_input():
    assert expected_calibration_error([], []) == 0.0
    assert brier_score([], []) == 0.0


def test_metrics_reject_mismatched_lengths():
    with pytest.raises(ValueError):
        brier_score([0.9, 0.8], [1])
    with pytest.raises(ValueError):
        reliability_bins([0.9, 0.8], [1])


def test_reliability_bins_group_by_confidence():
    scores = [0.05, 0.15, 0.95]
    outcomes = [0, 0, 1]
    bins = reliability_bins(scores, outcomes, n_bins=10)
    # Three distinct deciles occupied; empty bins are omitted.
    assert len(bins) == 3
    assert sum(b.count for b in bins) == 3


def test_reliability_bin_includes_score_of_exactly_one():
    bins = reliability_bins([1.0], [1], n_bins=10)
    assert len(bins) == 1
    assert bins[0].count == 1
    assert bins[0].upper == pytest.approx(1.0)


def test_reliability_bin_gap_sign_indicates_overconfidence():
    bins = reliability_bins([0.95, 0.95], [1, 0], n_bins=10)
    assert len(bins) == 1
    # Confidence 0.95 vs accuracy 0.50 -> positive gap = over-confident.
    assert bins[0].gap > 0.0


# --------------------------------------------------------------------------
# Calibrator behaviour
# --------------------------------------------------------------------------


def test_default_calibrator_is_identity():
    calibrator = ConfidenceCalibrator()
    assert calibrator.is_identity is True
    assert calibrator.fitted is False
    assert calibrator.temperature == 1.0
    for score in (0.0, 0.4550, 0.85, 0.9325, 1.0):
        assert calibrator.apply(score) == score


def test_identity_calibrator_clamps_out_of_range_input():
    calibrator = ConfidenceCalibrator()
    assert calibrator.apply(1.5) == 1.0
    assert calibrator.apply(-0.2) == 0.0


def test_calibrator_apply_all_is_vectorized():
    calibrator = ConfidenceCalibrator()
    assert calibrator.apply_all([0.1, 0.5, 0.9]) == [0.1, 0.5, 0.9]


def test_fit_corrects_systematic_overconfidence():
    """LLMs report ~0.95 confidence on findings that are right only half the
    time; a fitted calibrator must pull those scores down."""
    scores = [0.95] * 20
    outcomes = [1] * 10 + [0] * 10

    calibrator = ConfidenceCalibrator().fit(scores, outcomes)
    assert calibrator.fitted is True
    assert calibrator.sample_count == 20

    calibrated = calibrator.apply(0.95)
    assert calibrated < 0.95
    # The empirical accuracy is 0.5, so the calibrated score should approach it.
    assert calibrated == pytest.approx(0.5, abs=0.1)


def test_fit_reduces_expected_calibration_error():
    scores = [0.95] * 10 + [0.85] * 10
    outcomes = ([1] * 5 + [0] * 5) + ([1] * 5 + [0] * 5)

    uncalibrated_ece = expected_calibration_error(scores, outcomes)
    report = ConfidenceCalibrator().fit(scores, outcomes).evaluate(scores, outcomes)

    assert report.expected_calibration_error < uncalibrated_ece
    assert report.sample_count == 20


def test_fit_preserves_monotonicity():
    scores = [0.2, 0.4, 0.6, 0.8, 0.95]
    outcomes = [0, 0, 1, 1, 1]
    calibrator = ConfidenceCalibrator().fit(scores, outcomes)

    calibrated = calibrator.apply_all(scores)
    assert calibrated == sorted(calibrated)
    # A negative slope would invert the meaning of confidence.
    assert calibrator.a >= 0.0


def test_fit_on_low_variance_data_does_not_collapse_the_slope():
    """Regression: when every training score is identical the slope is
    unidentifiable and gradient descent drove it to zero, turning the
    calibrator into a constant that mapped every finding to one value and
    destroyed the ranking the audit queue prioritizes by."""
    calibrator = ConfidenceCalibrator().fit([0.95] * 20, [1] * 4 + [0] * 16)

    assert calibrator.a > 0.0
    assert calibrator.temperature != float("inf")

    # Distinct inputs must still produce distinct, correctly ordered outputs.
    low, high = calibrator.apply(0.30), calibrator.apply(0.99)
    assert low < high


def test_fit_keeps_ranking_intact_across_the_full_range():
    calibrator = ConfidenceCalibrator().fit([0.9] * 10, [0] * 10)
    probes = [0.1, 0.3, 0.5, 0.7, 0.9, 0.99]
    calibrated = calibrator.apply_all(probes)
    assert calibrated == sorted(calibrated)
    assert len(set(calibrated)) > 1


def test_fit_is_deterministic():
    scores = [0.9, 0.8, 0.7, 0.6]
    outcomes = [1, 1, 0, 0]
    first = ConfidenceCalibrator().fit(scores, outcomes)
    second = ConfidenceCalibrator().fit(scores, outcomes)
    assert (first.a, first.b) == (second.a, second.b)


def test_fit_on_empty_data_leaves_identity():
    calibrator = ConfidenceCalibrator().fit([], [])
    assert calibrator.is_identity is True
    assert calibrator.fitted is False


def test_fit_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        ConfidenceCalibrator().fit([0.9, 0.8], [1])


def test_calibration_report_is_serializable():
    scores = [0.95] * 10
    outcomes = [1] * 5 + [0] * 5
    payload = ConfidenceCalibrator().evaluate(scores, outcomes).as_dict()

    assert payload["sample_count"] == 10
    assert payload["expected_calibration_error"] == pytest.approx(0.45)
    assert len(payload["bins"]) == 1
    assert payload["bins"][0]["count"] == 10
