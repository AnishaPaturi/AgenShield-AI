import subprocess
import json
import sys
import os
from typing import List, Dict, Any, Union
from agentshield.parsers.schemas import ScanReport, CheckovFinding, ScanSummary

def run_checkov_scan(target_path: str, framework: str = "all") -> List[ScanReport]:
    """
    Runs Checkov scanner on the given path and parses the output.
    
    Args:
        target_path: Path to file or directory to scan.
        framework: IaC framework to scan (e.g. "terraform", "cloudformation", "kubernetes", or "all").
        
    Returns:
        List[ScanReport]: List of parsed scan reports (one per framework analyzed).
    """
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Target path does not exist: {target_path}")

    # Build python execution command to invoke checkov module.
    # We use sys.executable to ensure we run under the same virtualenv python interpreter.
    cmd = [sys.executable, "-m", "checkov.main", "--output", "json", "--quiet"]

    if os.path.isdir(target_path):
        cmd.extend(["-d", target_path])
    else:
        cmd.extend(["-f", target_path])

    if framework and framework != "all":
        cmd.extend(["--framework", framework])

    # Run checkov as subprocess.
    # Note: Checkov returns non-zero exit codes if findings are present, 
    # so we do not check return code via check=True. We only inspect stdout.
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    stdout_data = result.stdout.strip()
    if not stdout_data:
        if result.stderr:
            raise RuntimeError(f"Checkov scan execution error: {result.stderr}")
        return []

    try:
        raw_output = json.loads(stdout_data)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Failed to parse Checkov output as JSON: {e}\n"
            f"Raw stdout: {stdout_data[:500]}\n"
            f"Stderr: {result.stderr[:500]}"
        )

    # Checkov output can be a single dict (single framework scan) 
    # or a list of dicts (multiple framework scans)
    if isinstance(raw_output, dict):
        reports_data = [raw_output]
    elif isinstance(raw_output, list):
        reports_data = raw_output
    else:
        raise ValueError("Invalid format received from Checkov output")

    reports = []
    for rep in reports_data:
        check_type = rep.get("check_type", "unknown")
        
        sum_data = rep.get("summary", {})
        summary = ScanSummary(
            passed=sum_data.get("passed", 0),
            failed=sum_data.get("failed", 0),
            skipped=sum_data.get("skipped", 0),
            parsing_errors=sum_data.get("parsing_errors", 0),
            resource_count=sum_data.get("resource_count", 0),
            checkov_version=sum_data.get("checkov_version", "unknown")
        )

        findings = []
        results = rep.get("results", {})
        
        # Failed checks
        failed_checks = results.get("failed_checks", [])
        for check in failed_checks:
            finding = CheckovFinding(
                check_id=check.get("check_id", "unknown"),
                check_name=check.get("check_name", "unknown"),
                check_result="FAILED",
                file_path=check.get("file_path", ""),
                file_line_range=check.get("file_line_range", []),
                resource=check.get("resource", ""),
                severity=check.get("severity"),
                guideline=check.get("guideline"),
                code_block=check.get("code_block", [])
            )
            findings.append(finding)

        # Passed checks
        passed_checks = results.get("passed_checks", [])
        for check in passed_checks:
            finding = CheckovFinding(
                check_id=check.get("check_id", "unknown"),
                check_name=check.get("check_name", "unknown"),
                check_result="PASSED",
                file_path=check.get("file_path", ""),
                file_line_range=check.get("file_line_range", []),
                resource=check.get("resource", ""),
                severity=check.get("severity"),
                guideline=check.get("guideline"),
                code_block=check.get("code_block", [])
            )
            findings.append(finding)

        reports.append(ScanReport(
            check_type=check_type,
            findings=findings,
            summary=summary
        ))

    return reports
