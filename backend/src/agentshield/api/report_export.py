"""Report Generator — multi-format compliance-ready exports (Task 4.4).

Takes a completed `AgentShieldWorkspace` and renders it as:
    - JSON      machine-readable, full fidelity
    - Markdown  human-readable, PR/ticket friendly
    - HTML      standalone styled report, viewable in any browser
    - SARIF     for GitHub Security tab / code scanning ingestion
    - PDF       executive-summary style document

Each `render_*` function is pure (workspace in, bytes/str out) so it can be
called from the API layer, a CLI, or a test — no I/O or FastAPI dependency.
"""

from __future__ import annotations

import io
import json
from datetime import UTC, datetime

from agentshield.core.schemas import AgentShieldWorkspace, Severity

SEVERITY_ORDER = [
    Severity.CRITICAL,
    Severity.HIGH,
    Severity.MEDIUM,
    Severity.LOW,
    Severity.INFORMATIONAL,
]

# SARIF severity levels: error | warning | note | none
_SARIF_LEVEL = {
    Severity.CRITICAL: "error",
    Severity.HIGH: "error",
    Severity.MEDIUM: "warning",
    Severity.LOW: "note",
    Severity.INFORMATIONAL: "none",
}


def render_json(workspace: AgentShieldWorkspace) -> str:
    """Full-fidelity JSON export of the workspace."""
    return workspace.model_dump_json(indent=2)


def render_markdown(workspace: AgentShieldWorkspace) -> str:
    report = workspace.report
    lines: list[str] = []
    lines.append(f"# AgentShield AI — Security Report")
    lines.append("")
    lines.append(f"**Target file:** `{workspace.template.file_path}`  ")
    lines.append(f"**IaC type:** {workspace.template.iac_type.value}  ")
    lines.append(f"**Cloud provider:** {workspace.template.cloud_provider.value}  ")
    lines.append(f"**Workspace ID:** `{workspace.workspace_id}`  ")
    lines.append(f"**Generated:** {datetime.now(UTC).isoformat()}")
    lines.append("")

    if report is None:
        lines.append("_No analysis has been run for this workspace yet._")
        return "\n".join(lines)

    s = report.summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Risk score:** {s.risk_score} / 100")
    lines.append(f"- **Total findings:** {s.total_vulnerabilities}")
    lines.append(
        f"- Critical: {s.critical_count} · High: {s.high_count} · "
        f"Medium: {s.medium_count} · Low: {s.low_count} · Info: {s.info_count}"
    )
    lines.append("")
    lines.append("## Findings")
    lines.append("")

    patches_by_finding = {p.finding_id: p for p in workspace.patches}

    ordered = sorted(report.findings, key=lambda f: SEVERITY_ORDER.index(f.severity))
    for f in ordered:
        lines.append(f"### [{f.severity.value}] {f.title}  (`{f.rule_id}`)")
        lines.append("")
        lines.append(f"{f.description}")
        lines.append("")
        lines.append(f"- **Affected resource:** `{f.affected_resource}`")
        if f.resource_type:
            lines.append(f"- **Resource type:** `{f.resource_type}`")
        lines.append(f"- **Confidence:** {f.confidence_score}")
        if f.compliance_mappings:
            mappings = ", ".join(
                f"{m.framework.value}:{m.control_id}" for m in f.compliance_mappings
            )
            lines.append(f"- **Compliance:** {mappings}")
        if f.attack_path:
            lines.append(f"- **Attack path:** {' → '.join(f.attack_path)}")
        if f.remediation_hint:
            lines.append(f"- **Remediation hint:** {f.remediation_hint}")

        patch = patches_by_finding.get(f.finding_id)
        if patch:
            lines.append("")
            lines.append(f"**Suggested patch** (status: `{patch.remediation_status.value}`):")
            lines.append("")
            lines.append("```diff")
            lines.append(patch.unified_diff.rstrip() or "(no diff generated)")
            lines.append("```")
        lines.append("")

    return "\n".join(lines)


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AgentShield AI Report — {file_path}</title>
<style>
  :root {{ color-scheme: light; }}
  body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; max-width: 900px;
          margin: 40px auto; padding: 0 20px; color: #1a1a1a; background: #fafafa; }}
  h1 {{ font-size: 1.6rem; }}
  .meta {{ color: #555; font-size: 0.9rem; margin-bottom: 24px; }}
  .summary {{ display: flex; gap: 12px; flex-wrap: wrap; margin: 20px 0 32px; }}
  .stat {{ background: #fff; border: 1px solid #e2e2e2; border-radius: 8px; padding: 12px 18px; }}
  .stat .n {{ font-size: 1.4rem; font-weight: 700; display: block; }}
  .finding {{ background: #fff; border: 1px solid #e2e2e2; border-radius: 10px;
              padding: 18px 20px; margin-bottom: 16px; }}
  .badge {{ display: inline-block; padding: 2px 10px; border-radius: 999px;
            font-size: 0.75rem; font-weight: 700; color: #fff; }}
  .CRITICAL {{ background: #b91c1c; }}
  .HIGH {{ background: #ea580c; }}
  .MEDIUM {{ background: #ca8a04; }}
  .LOW {{ background: #2563eb; }}
  .INFORMATIONAL {{ background: #6b7280; }}
  pre {{ background: #0d1117; color: #e6edf3; padding: 12px; border-radius: 8px;
         overflow-x: auto; font-size: 0.85rem; }}
  code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
</style>
</head>
<body>
  <h1>AgentShield AI — Security Report</h1>
  <div class="meta">
    Target: <code>{file_path}</code> &nbsp;·&nbsp; IaC: {iac_type} &nbsp;·&nbsp;
    Cloud: {cloud_provider} &nbsp;·&nbsp; Generated: {generated_at}
  </div>
  <div class="summary">
    <div class="stat"><span class="n">{risk_score}</span>Risk score / 100</div>
    <div class="stat"><span class="n">{total}</span>Total findings</div>
    <div class="stat"><span class="n">{critical}</span>Critical</div>
    <div class="stat"><span class="n">{high}</span>High</div>
    <div class="stat"><span class="n">{medium}</span>Medium</div>
    <div class="stat"><span class="n">{low}</span>Low</div>
  </div>
  {findings_html}
</body>
</html>
"""

_FINDING_TEMPLATE = """
  <div class="finding">
    <span class="badge {severity}">{severity}</span>
    <strong>{title}</strong> <code>{rule_id}</code>
    <p>{description}</p>
    <p><em>Affected resource:</em> <code>{affected_resource}</code> &nbsp; <em>Confidence:</em> {confidence}</p>
    {patch_html}
  </div>
"""


def render_html(workspace: AgentShieldWorkspace) -> str:
    report = workspace.report
    patches_by_finding = {p.finding_id: p for p in workspace.patches}

    if report is None:
        findings_html = "<p><em>No analysis has been run for this workspace yet.</em></p>"
        s_total = s_crit = s_high = s_med = s_low = 0
        risk = 0.0
    else:
        ordered = sorted(report.findings, key=lambda f: SEVERITY_ORDER.index(f.severity))
        blocks = []
        for f in ordered:
            patch = patches_by_finding.get(f.finding_id)
            patch_html = ""
            if patch:
                diff = (patch.unified_diff or "").replace("<", "&lt;").replace(">", "&gt;")
                patch_html = f"<pre><code>{diff}</code></pre>"
            blocks.append(
                _FINDING_TEMPLATE.format(
                    severity=f.severity.value,
                    title=f.title,
                    rule_id=f.rule_id,
                    description=f.description,
                    affected_resource=f.affected_resource,
                    confidence=f.confidence_score,
                    patch_html=patch_html,
                )
            )
        findings_html = "\n".join(blocks)
        s = report.summary
        s_total, s_crit, s_high, s_med, s_low = (
            s.total_vulnerabilities,
            s.critical_count,
            s.high_count,
            s.medium_count,
            s.low_count,
        )
        risk = s.risk_score

    return _HTML_TEMPLATE.format(
        file_path=workspace.template.file_path,
        iac_type=workspace.template.iac_type.value,
        cloud_provider=workspace.template.cloud_provider.value,
        generated_at=datetime.now(UTC).isoformat(),
        risk_score=risk,
        total=s_total,
        critical=s_crit,
        high=s_high,
        medium=s_med,
        low=s_low,
        findings_html=findings_html,
    )


def render_sarif(workspace: AgentShieldWorkspace) -> str:
    """SARIF 2.1.0 export, ingestible by GitHub's code-scanning / Security tab."""
    report = workspace.report
    findings = report.findings if report else []

    rules = {}
    results = []
    for f in findings:
        if f.rule_id not in rules:
            rules[f.rule_id] = {
                "id": f.rule_id,
                "name": f.title,
                "shortDescription": {"text": f.title},
                "fullDescription": {"text": f.description},
                "helpUri": "https://github.com/agentshield-ai",
                "properties": {"severity": f.severity.value},
            }

        region = {}
        if f.line_range:
            region = {"startLine": f.line_range.start_line, "endLine": f.line_range.end_line}

        results.append(
            {
                "ruleId": f.rule_id,
                "level": _SARIF_LEVEL.get(f.severity, "warning"),
                "message": {"text": f.description},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": workspace.template.file_path},
                            **({"region": region} if region else {}),
                        }
                    }
                ],
                "properties": {
                    "confidence": f.confidence_score,
                    "affected_resource": f.affected_resource,
                    "compliance": [
                        f"{m.framework.value}:{m.control_id}" for m in f.compliance_mappings
                    ],
                },
            }
        )

    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "AgentShield AI",
                        "informationUri": "https://github.com/agentshield-ai",
                        "version": "0.1.0",
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
            }
        ],
    }
    return json.dumps(sarif, indent=2)


def render_pdf(workspace: AgentShieldWorkspace) -> bytes:
    """Executive-summary PDF export using reportlab (pure-Python, no system deps)."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER, title="AgentShield AI Report")
    styles = getSampleStyleSheet()
    h1 = styles["Heading1"]
    h2 = styles["Heading2"]
    body = styles["BodyText"]
    small = ParagraphStyle("small", parent=body, fontSize=8, textColor=colors.grey)

    story = [
        Paragraph("AgentShield AI — Security Report", h1),
        Paragraph(f"Target file: {workspace.template.file_path}", body),
        Paragraph(
            f"IaC type: {workspace.template.iac_type.value} &nbsp;|&nbsp; "
            f"Cloud: {workspace.template.cloud_provider.value}",
            body,
        ),
        Paragraph(f"Generated: {datetime.now(UTC).isoformat()}", small),
        Spacer(1, 0.25 * inch),
    ]

    report = workspace.report
    if report is None:
        story.append(Paragraph("No analysis has been run for this workspace yet.", body))
    else:
        s = report.summary
        story.append(Paragraph("Executive Summary", h2))
        summary_table = Table(
            [
                ["Risk Score", "Total", "Critical", "High", "Medium", "Low"],
                [
                    s.risk_score,
                    s.total_vulnerabilities,
                    s.critical_count,
                    s.high_count,
                    s.medium_count,
                    s.low_count,
                ],
            ],
            hAlign="LEFT",
        )
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            )
        )
        story.append(summary_table)
        story.append(Spacer(1, 0.25 * inch))

        story.append(Paragraph("Findings", h2))
        ordered = sorted(report.findings, key=lambda f: SEVERITY_ORDER.index(f.severity))
        for f in ordered:
            story.append(
                Paragraph(f"<b>[{f.severity.value}] {f.title}</b> ({f.rule_id})", body)
            )
            story.append(Paragraph(f.description, body))
            story.append(
                Paragraph(
                    f"Affected resource: {f.affected_resource} | Confidence: {f.confidence_score}",
                    small,
                )
            )
            story.append(Spacer(1, 0.12 * inch))

    doc.build(story)
    return buf.getvalue()


RENDERERS = {
    "json": render_json,
    "markdown": render_markdown,
    "md": render_markdown,
    "html": render_html,
    "sarif": render_sarif,
    "pdf": render_pdf,
}

MEDIA_TYPES = {
    "json": "application/json",
    "markdown": "text/markdown",
    "md": "text/markdown",
    "html": "text/html",
    "sarif": "application/sarif+json",
    "pdf": "application/pdf",
}
