"""AgentShield AI Git Pre-Commit Hook (Task 5.1).

Scans staged Infrastructure-as-Code files before commits are recorded,
intercepting hardcoded credentials, high-severity misconfigurations,
and optionally applying validated patches via `--fix`.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from agentshield.agents import RemediationAgent, SecurityAnalystAgent, ValidatorAgent
from agentshield.agents.secrets import SecretsScannerAgent
from agentshield.api.orchestrator import build_iac_template
from agentshield.core.schemas import (
    IaCTemplate,
    RemediationStatus,
    Severity,
)

TARGET_EXTENSIONS = {".tf", ".yaml", ".yml", ".json"}


def get_git_staged_content(file_path: Path) -> str | None:
    """Retrieve staged content from git index if file is tracked in git.

    Returns None if git is not available or file is not staged.
    """
    try:
        rel_path = file_path.as_posix()
        # git show :path reads directly from the git index (staged version)
        result = subprocess.run(
            ["git", "show", f":{rel_path}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if result.returncode == 0:
            return result.stdout
    except Exception:
        pass
    return None


def scan_file(
    file_path: Path,
    strict: bool = False,
    auto_fix: bool = False,
    staged_content: str | None = None,
) -> tuple[bool, list[str], str | None]:
    """Scan an individual IaC file for secrets and vulnerabilities.

    Args:
        file_path: Path to the target IaC template.
        strict: When True, blocks Medium severity findings in addition to Critical/High/Secrets.
        auto_fix: When True, synthesizes and applies validated patch diffs.
        staged_content: Optional in-memory staged content to evaluate instead of disk content.

    Returns:
        (passed, issues_list, patched_content_if_fixed)
    """
    issues: list[str] = []

    # 1. Resolve raw content (staged vs disk)
    if staged_content is not None:
        raw_content = staged_content
    else:
        if not file_path.exists() or file_path.is_dir():
            return True, [], None
        raw_content = file_path.read_text(encoding="utf-8", errors="replace")

    if not raw_content.strip():
        return True, [], None

    # Check extension
    if file_path.suffix.lower() not in TARGET_EXTENSIONS:
        return True, [], None

    try:
        template = build_iac_template(str(file_path), raw_content.encode("utf-8"))
    except Exception as exc:
        # Scanner fail-safe: parsing failure must fail safe rather than silently allowing insecure code
        issues.append(f"[PARSER_ERROR] Failed to parse {file_path.name}: {exc}")
        return False, issues, None

    # 2. Run Secrets Interceptor (Agent 3)
    secrets_found = []
    try:
        secrets_agent = SecretsScannerAgent()
        secrets_found = secrets_agent.scan(str(file_path), content=raw_content)
        for s in secrets_found:
            issues.append(f"[SECRET] {s.title} ({s.rule_id}) - {s.description}")
    except Exception as exc:
        issues.append(f"[SCANNER_ERROR] Secrets scanner failed: {exc}")
        return False, issues, None

    # 3. Run Polyglot AST Parsing & Static/Heuristic Security Analysis
    try:
        analyst = SecurityAnalystAgent()
        report = analyst.analyze(template)
    except Exception as exc:
        issues.append(f"[SCANNER_ERROR] Security analyst evaluation failed: {exc}")
        return False, issues, None

    blocking_severities = {Severity.CRITICAL, Severity.HIGH}
    is_strict = strict or os.getenv("AGENTSHIELD_STRICT", "").lower() in {"1", "true", "yes"}
    if is_strict:
        blocking_severities.add(Severity.MEDIUM)

    blocking_findings = [f for f in report.findings if f.severity in blocking_severities]
    for f in blocking_findings:
        issues.append(
            f"[{f.severity.value}] {f.title} ({f.rule_id}) at {f.affected_resource}"
        )

    # Informational / non-blocking warnings
    non_blocking = [f for f in report.findings if f.severity not in blocking_severities]
    for f in non_blocking:
        # Warnings logged for visibility without blocking commit
        print(f"       ⚠️  [ADVISORY: {f.severity.value}] {f.title} ({f.rule_id})")

    # 4. Optional Auto-Fix with Remediation & Validation Harness
    patched_content: str | None = None
    if auto_fix and blocking_findings and not secrets_found:
        remediator = RemediationAgent()
        validator = ValidatorAgent()
        current_content = raw_content

        for f in blocking_findings:
            if not f.auto_patchable:
                continue
            try:
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
            except Exception:
                # If auto-fix fails, retain finding as blocking
                pass

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
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Read staged content directly from the git index.",
    )

    args = parser.parse_args(argv)

    files_to_scan: list[Path] = []
    for f_str in args.filenames:
        p = Path(f_str)
        if p.suffix.lower() in TARGET_EXTENSIONS:
            # If checking staged or disk
            if p.is_file() or args.staged:
                files_to_scan.append(p)

    if not files_to_scan:
        # No relevant IaC files staged: fast-path exit 0
        return 0

    has_failures = False
    print("\n🛡️  AgentShield AI Pre-Commit IaC Security Scanner")
    print("=" * 60)

    for file_path in files_to_scan:
        staged_content = None
        if args.staged:
            staged_content = get_git_staged_content(file_path)

        passed, issues, patched_content = scan_file(
            file_path,
            strict=args.strict,
            auto_fix=args.fix,
            staged_content=staged_content,
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
