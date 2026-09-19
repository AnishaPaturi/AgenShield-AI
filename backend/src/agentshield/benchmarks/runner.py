"""Benchmark Runner executing evaluations across the benchmark corpus (Task 5.3)."""

from __future__ import annotations

import time

from agentshield.agents import RemediationAgent, SecurityAnalystAgent, ValidatorAgent
from agentshield.benchmarks.corpus import BenchmarkCase, get_standard_benchmark_corpus
from agentshield.benchmarks.metrics import BenchmarkMetrics
from agentshield.core.schemas import (
    IaCTemplate,
    RemediationStatus,
)


class BenchmarkRunner:
    """Executes automated benchmark evaluations measuring precision, recall, and patch pass rate."""

    def __init__(
        self,
        analyst: SecurityAnalystAgent | None = None,
        remediator: RemediationAgent | None = None,
        validator: ValidatorAgent | None = None,
    ) -> None:
        self.analyst = analyst or SecurityAnalystAgent()
        self.remediator = remediator or RemediationAgent()
        self.validator = validator or ValidatorAgent()

    def run_benchmark(
        self,
        corpus: list[BenchmarkCase] | None = None,
        validate_patches: bool = True,
    ) -> BenchmarkMetrics:
        cases = corpus if corpus is not None else get_standard_benchmark_corpus()
        metrics = BenchmarkMetrics(total_cases=len(cases))

        for case in cases:
            template = IaCTemplate(
                file_path=f"benchmarks/{case.case_id}.tf",
                raw_content=case.content,
                iac_type=case.iac_type,
                cloud_provider=case.cloud_provider,
            )

            start_t = time.perf_counter()
            report = self.analyst.analyze(template)
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            metrics.latencies_ms.append(elapsed_ms)

            detected_rules = {f.rule_id for f in report.findings}
            has_findings = len(report.findings) > 0

            # Evaluate Detection Accuracy against ground truth
            if case.is_vulnerable:
                if has_findings:
                    metrics.true_positives += 1
                else:
                    metrics.false_negatives += 1
            else:
                if has_findings:
                    metrics.false_positives += 1
                else:
                    metrics.true_negatives += 1

            # Evaluate Patch Generation & Validation
            if validate_patches and has_findings:
                patches = self.remediator.generate_patches(template, report)
                metrics.patches_generated += len(patches)

                validated_patches = self.validator.validate_patches(
                    template=template,
                    patches=patches,
                    report=report,
                    remediator=self.remediator,
                )
                valid_count = sum(
                    1
                    for p in validated_patches
                    if p.remediation_status
                    in {RemediationStatus.SYNTAX_VALIDATED, RemediationStatus.SANDBOX_PASSED}
                )
                metrics.patches_validated += valid_count

        return metrics
