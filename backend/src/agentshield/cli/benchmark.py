"""Command-line interface for running benchmarks and ablation studies (Task 5.3)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agentshield.benchmarks import (
    AblationStudyEngine,
    BenchmarkRunner,
    generate_ablation_markdown_report,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agentshield.cli.benchmark",
        description="Run automated empirical benchmark evaluations & ablation studies.",
    )
    parser.add_argument(
        "--ablation",
        action="store_true",
        help="Execute all 4 controlled ablation studies.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="",
        help="Path to save generated markdown ablation report.",
    )

    args = parser.parse_args(argv)

    print("\n🔬 AgentShield AI — Empirical Benchmark Evaluation Harness")
    print("=" * 65)

    if args.ablation:
        print("Running 4 Component Ablation Studies against vulnerable IaC corpora...")
        engine = AblationStudyEngine()
        results = engine.run_all_ablation_studies()
        report_md = generate_ablation_markdown_report(results)
        print("\n" + report_md)

        if args.output:
            out_file = Path(args.output)
            out_file.write_text(report_md, encoding="utf-8")
            print(f"Report saved to: {out_file.resolve()}")
    else:
        print("Running benchmark suite on standard corpus...")
        runner = BenchmarkRunner()
        metrics = runner.run_benchmark(validate_patches=True)
        print("\nBenchmark Evaluation Results:")
        for k, v in metrics.to_dict().items():
            print(f"  • {k}: {v}")

    print("=" * 65)
    print("✅ Benchmark execution finished successfully.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
