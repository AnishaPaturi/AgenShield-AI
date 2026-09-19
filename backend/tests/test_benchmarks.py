"""Unit tests for Empirical Benchmark Suite & Ablation Studies (Task 5.3)."""

from pathlib import Path

from agentshield.benchmarks import (
    AblationStudyEngine,
    BenchmarkMetrics,
    BenchmarkRunner,
    generate_ablation_markdown_report,
    get_standard_benchmark_corpus,
)
from agentshield.cli.benchmark import main


def test_benchmark_corpus_loaded():
    corpus = get_standard_benchmark_corpus()
    assert len(corpus) >= 5
    # Verify both vulnerable and benign cases exist
    vulnerable_cases = [c for c in corpus if c.is_vulnerable]
    benign_cases = [c for c in corpus if not c.is_vulnerable]
    assert len(vulnerable_cases) >= 4
    assert len(benign_cases) >= 2


def test_benchmark_metrics_calculations():
    metrics = BenchmarkMetrics(
        total_cases=10,
        true_positives=8,
        false_positives=1,
        false_negatives=0,
        true_negatives=1,
        patches_generated=8,
        patches_validated=8,
        latencies_ms=[100.0, 200.0, 300.0],
    )

    # Precision: 8 / (8 + 1) = 0.8889
    assert metrics.precision == 0.8889
    # Recall: 8 / (8 + 0) = 1.0
    assert metrics.recall == 1.0
    # F1: 2 * (0.8889 * 1.0) / (0.8889 + 1.0) = 0.9412
    assert metrics.f1_score == 0.9412
    # Hallucination Rate: 1 / 9 = 0.1111
    assert metrics.hallucination_rate == 0.1111
    # Patch Pass Rate: 8 / 8 = 1.0
    assert metrics.patch_pass_rate == 1.0
    # Mean Latency: 200.0
    assert metrics.mean_latency_ms == 200.0

    d = metrics.to_dict()
    assert d["total_cases"] == 10
    assert d["precision"] == 0.8889


def test_benchmark_runner_execution():
    corpus = get_standard_benchmark_corpus()[:3]
    runner = BenchmarkRunner()
    metrics = runner.run_benchmark(corpus=corpus, validate_patches=True)

    assert metrics.total_cases == 3
    assert metrics.true_positives >= 1
    assert metrics.precision > 0.0
    assert metrics.patch_pass_rate > 0.0


def test_ablation_study_engine():
    engine = AblationStudyEngine()
    studies = engine.run_all_ablation_studies()

    assert len(studies) == 4
    study_names = [s.study_name for s in studies]
    assert any("Baseline Comparison" in name for name in study_names)
    assert any("RAG Context" in name for name in study_names)
    assert any("Ensemble" in name for name in study_names)
    assert any("AST" in name for name in study_names)

    # Generate report
    report_md = generate_ablation_markdown_report(studies)
    assert "AgentShield AI — Empirical Benchmark & Ablation Study Report" in report_md
    assert "Precision" in report_md
    assert "F1-Score" in report_md
    assert "Hallucination Rate" in report_md


def test_benchmark_cli_main(tmp_path: Path):
    out_file = tmp_path / "ablation_report.md"
    exit_code = main(["--ablation", "--output", str(out_file)])
    assert exit_code == 0
    assert out_file.exists()
    assert len(out_file.read_text(encoding="utf-8")) > 100
