import os
from agentshield.utils import run_checkov_scan
from agentshield.parsers.schemas import ScanReport, CheckovFinding

def test_run_checkov_scan_success():
    # Define target path (relative to the backend directory, where pytest is run)
    target_path = "./infrastructure/terraform"
    assert os.path.exists(target_path), f"Test path does not exist: {target_path}"
    
    # Run the scan
    reports = run_checkov_scan(target_path, framework="terraform")
    
    # Assert reports were generated
    assert isinstance(reports, list)
    assert len(reports) > 0
    
    report = reports[0]
    assert isinstance(report, ScanReport)
    assert report.check_type == "terraform"
    
    # Assert findings are parsed properly
    assert len(report.findings) > 0
    assert any(f.check_result == "FAILED" for f in report.findings)
    
    # Validate a sample finding contains expected attributes
    sample_finding = [f for f in report.findings if f.check_result == "FAILED"][0]
    assert sample_finding.check_id.startswith("CKV")
    assert sample_finding.check_name != ""
    assert sample_finding.file_path != ""
    assert sample_finding.resource != ""
    
    # Assert summary is parsed
    assert report.summary.failed > 0
    assert report.summary.resource_count == 2  # aws_s3_bucket + public_access_block
