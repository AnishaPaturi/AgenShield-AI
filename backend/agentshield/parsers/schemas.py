from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class CheckovFinding(BaseModel):
    check_id: str
    check_name: str
    check_result: str  # e.g. "FAILED", "PASSED"
    file_path: str
    file_line_range: List[int] = Field(default_factory=list)
    resource: str
    severity: Optional[str] = None
    guideline: Optional[str] = None
    code_block: List[List[Any]] = Field(default_factory=list)

class ScanSummary(BaseModel):
    passed: int
    failed: int
    skipped: int
    parsing_errors: int
    resource_count: int
    checkov_version: str

class ScanReport(BaseModel):
    check_type: str
    findings: List[CheckovFinding] = Field(default_factory=list)
    summary: ScanSummary
