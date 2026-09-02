"""Tests for LLM Client, Structured Parsing, and Multi-LLM Ensemble."""

import json

from pydantic import BaseModel, Field

from agentshield.core.llm import LLMClient, LLMConfig, LLMProvider, MultiLLMEnsemble


class SampleSchema(BaseModel):
    name: str = Field(...)
    score: float = Field(...)


def test_llm_config_defaults():
    config = LLMConfig()
    assert config.provider == LLMProvider.MOCK
    assert config.model_name == "gpt-4o"
    assert config.temperature == 0.0


def test_mock_llm_generate():
    client = LLMClient()
    client.set_mock_responses(["Hello World Response"])
    res = client.generate("Say hello")
    assert res.content == "Hello World Response"
    assert res.provider == LLMProvider.MOCK


def test_llm_generate_structured():
    client = LLMClient()
    mock_json = json.dumps({"name": "Test Finding", "score": 0.95})
    client.set_mock_responses([f"```json\n{mock_json}\n```"])

    parsed = client.generate_structured("Extract data", SampleSchema)
    assert isinstance(parsed, SampleSchema)
    assert parsed.name == "Test Finding"
    assert parsed.score == 0.95


def test_multi_llm_ensemble_confidence():
    client1 = LLMClient()
    client2 = LLMClient()
    ensemble = MultiLLMEnsemble([client1, client2])

    confidence_full = ensemble.compute_consensus_confidence(
        agreed_count=2, total_models=2, base_confidence=0.8
    )
    assert confidence_full == 0.8  # 0.8 * (0.5 + 0.5 * 1.0) = 0.8

    confidence_partial = ensemble.compute_consensus_confidence(
        agreed_count=1, total_models=2, base_confidence=0.8
    )
    assert confidence_partial == 0.6  # 0.8 * (0.5 + 0.5 * 0.5) = 0.6


def test_calibrated_confidence_scoring_dual_models():
    client1 = LLMClient()
    client2 = LLMClient()
    ensemble = MultiLLMEnsemble([client1, client2])

    # Both models agree on vulnerability with C=0.90, full line overlap S=1.0
    # C_ensemble = 0.45(0.90) + 0.45(0.90) + 0.10(1.0)(2/2) = 0.405 + 0.405 + 0.10 = 0.9100
    score_both = ensemble.calculate_calibrated_confidence(
        model_confidences=[0.90, 0.90], total_models=2, agreement_score=1.0
    )
    assert score_both == 0.91
    auto_patchable, requires_review, reason = MultiLLMEnsemble.evaluate_routing(score_both)
    assert auto_patchable is True
    assert requires_review is False
    assert reason is None


def test_calibrated_confidence_eliminates_single_model_hallucination():
    client1 = LLMClient()
    client2 = LLMClient()
    ensemble = MultiLLMEnsemble([client1, client2])

    # Only 1 model flags finding with C=0.90 (single-model hallucination or uncertainty)
    # C_ensemble = 0.45(0.90) + 0.10(1.0)(1/2) = 0.405 + 0.05 = 0.4550 < 0.85
    score_single = ensemble.calculate_calibrated_confidence(
        model_confidences=[0.90], total_models=2, agreement_score=1.0
    )
    assert score_single == 0.455
    auto_patchable, requires_review, reason = MultiLLMEnsemble.evaluate_routing(score_single)
    assert auto_patchable is False
    assert requires_review is True
    assert reason is not None
    assert "below auto-patch threshold" in reason


def test_evaluate_routing_boundary_thresholds():
    # Exactly at threshold 0.85
    auto_p, req_rev, reason = MultiLLMEnsemble.evaluate_routing(0.85)
    assert auto_p is True
    assert req_rev is False
    assert reason is None

    # Just below threshold 0.8499
    auto_p, req_rev, reason = MultiLLMEnsemble.evaluate_routing(0.8499)
    assert auto_p is False
    assert req_rev is True
    assert "below auto-patch threshold 0.85" in reason
