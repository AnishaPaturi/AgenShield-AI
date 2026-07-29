"""
Command Line Interface (CLI) for AgentShield AI.
"""

import os
import sys
import click
from agentshield.graph import AgentShieldOrchestrator


@click.group()
def cli():
    """AgentShield AI - Multi-Cloud IaC Security & 8-Agent LangGraph Framework"""
    pass


@cli.command()
@click.option("--path", "-p", required=True, help="Path to IaC template file or directory to scan.")
@click.option("--output", "-o", default="", help="Optional output filepath for final security report.")
def scan(path: str, output: str):
    """Run the 8-agent LangGraph orchestration state machine scan."""
    click.echo(f"[SCAN] Starting AgentShield AI Scan on: {path}")
    if not os.path.exists(path):
        click.echo(f"[ERROR] Error: Path '{path}' does not exist.", err=True)
        sys.exit(1)

    orchestrator = AgentShieldOrchestrator()
    result = orchestrator.run(path)

    click.echo("\n=== Execution Log ===")
    for log in result.get("execution_log", []):
        click.echo(log)

    report_text = result.get("final_report", "")
    click.echo("\n" + report_text)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(report_text)
        click.echo(f"[SUCCESS] Security report exported to: {output}")


@cli.command()
def info():
    """Display system architecture and 8 specialized agents."""
    click.echo("""
AgentShield AI Autonomous 8-Agent Framework:
--------------------------------------------------
1. Manager/Router Agent      : Workload & execution state orchestration
2. Hybrid AST Parser Agent   : AST extraction across HCL, CFN, K8s, Helm
3. Secrets Scanner Agent     : Hardcoded credential & token leak interception
4. RAG-Query Agent           : Regulatory compliance rules (SOC2, HIPAA, PCI-DSS, NIST 800-53)
5. Security Analyst Agent    : Multi-LLM Ensemble Voting & confidence scoring
6. Remediation Agent         : Executable code diff-patch generation
7. Code & Sandbox Validator  : Static linting & LocalStack runtime sandbox testing
8. Report Agent              : Audit-ready compliance reporting & feedback logger
""")


def main():
    cli()


if __name__ == "__main__":
    main()
