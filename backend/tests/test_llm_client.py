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
