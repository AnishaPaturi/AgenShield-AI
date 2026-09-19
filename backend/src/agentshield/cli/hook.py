"""AgentShield AI Git Pre-Commit Hook (Task 5.1).

Scans staged Infrastructure-as-Code files before commits are recorded,
intercepting hardcoded credentials, high-severity misconfigurations,
and optionally applying validated patches via `--fix`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from agentshield.agents import RemediationAgent, SecurityAnalystAgent, ValidatorAgent
from agentshield.api.orchestrator import build_iac_template
from agentshield.core.schemas import (
    IaCTemplate,
    RemediationStatus,
    Severity,
)
from agentshield.agents.secrets import SecretsScannerAgent


def scan_file(
    file_path: Path,
    strict: bool = False,
    auto_fix: bool = False,
) -> tuple[bool, list[str], str | None]:
    """Scan an individual IaC file for secrets and vulnerabilities.

    Returns:
        (passed, issues_list, patched_content_if_fixed)
    """
    if not file_path.exists() or file_path.is_dir():
        return True, [], None

    raw_content = file_path.read_text(encoding="utf-8", errors="replace")
    if not raw_content.strip():
        return True, [], None

    template = build_iac_template(str(file_path), raw_content.encode("utf-8"))

    issues: list[str] = []

    # 1. Run Secrets Interceptor (Agent 3)
    secrets_agent = SecretsScannerAgent()
    secrets_found = secrets_agent.scan(str(file_path), content=raw_content)
    for s in secrets_found:
        issues.append(f"[SECRET] {s.title} ({s.rule_id}) - {s.description}")

    # 2. Run Polyglot AST Parsing & Static/Heuristic Security Analysis
    analyst = SecurityAnalystAgent()
    report = analyst.analyze(template)

    blocking_severities = {Severity.CRITICAL, Severity.HIGH}
    if strict:
        blocking_severities.add(Severity.MEDIUM)

    blocking_findings = [f for f in report.findings if f.severity in blocking_severities]
    for f in blocking_findings:
        issues.append(
            f"[{f.severity.value}] {f.title} ({f.rule_id}) at {f.affected_resource}"
        )

    # 3. Optional Auto-Fix with Remediation & Validation Harness
    patched_content: str | None = None
    if auto_fix and blocking_findings and not secrets_found:
        remediator = RemediationAgent()
        validator = ValidatorAgent()
        current_content = raw_content

        for f in blocking_findings:
            if not f.auto_patchable:
                continue
            patch = remediator.generate_patch(template, f)
            validated_patch = validator.validate_patch(
                template=template,
                patch=patch,
                finding=f,
                remediator=remediator,
            )
            if validated_patch.remediation_status in {
                RemediationStatus.SYNTAX_VALIDATED,
                RemediationStatus.SANDBOX_PASSED,
            }:
                # Apply fix
                if validated_patch.original_code in current_content:
                    current_content = current_content.replace(
                        validated_patch.original_code, validated_patch.patched_code, 1
                    )

        if current_content != raw_content:
            patched_content = current_content

    passed = len(issues) == 0 or (patched_content is not None and len(secrets_found) == 0)
    return passed, issues, patched_content


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agentshield.cli.hook",
        description="AgentShield AI Git Pre-Commit Hook for IaC templates.",
    )
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Files to scan (typically supplied automatically by pre-commit).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Block on Medium severity findings in addition to Critical/High and Secrets.",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically apply validated code diff patches to fix detected vulnerabilities.",
    )

    args = parser.parse_args(argv)

    target_extensions = {".tf", ".yaml", ".yml", ".json"}
    files_to_scan: list[Path] = []

    for f_str in args.filenames:
        p = Path(f_str)
        if p.suffix.lower() in target_extensions and p.is_file():
            files_to_scan.append(p)

    if not files_to_scan:
        # No relevant IaC files staged
        return 0

    has_failures = False
    print("\n🛡️  AgentShield AI Pre-Commit IaC Security Scanner")
    print("=" * 60)

    for file_path in files_to_scan:
        passed, issues, patched_content = scan_file(
            file_path, strict=args.strict, auto_fix=args.fix
        )

        if passed:
            if patched_content is not None:
                file_path.write_text(patched_content, encoding="utf-8")
                print(f"  🔧 [AUTO-FIXED] {file_path}")
            else:
                print(f"  ✅ [PASSED]     {file_path}")
        else:
            has_failures = True
            print(f"  ❌ [BLOCKED]    {file_path}")
            for issue in issues:
                print(f"       • {issue}")

    print("=" * 60)
    if has_failures:
        print("❌ Commit blocked: Fix reported security issues or re-run with --fix.\n")
        return 1

    print("✅ All staged IaC templates passed security checks.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
