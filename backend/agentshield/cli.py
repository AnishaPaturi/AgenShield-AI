import click
import os
from agentshield.utils.checkov_runner import run_checkov_scan

@click.group()
def main():
    """AgentShield AI - Multi-Agent Framework for Infrastructure-as-Code Security"""
    pass

@main.command()
@click.option('--path', '-p', required=True, type=click.Path(exists=True), help='Path to IaC files or directory to scan')
@click.option('--framework', '-f', default="all", help='Specific IaC framework to scan (terraform, cloudformation, kubernetes, all)')
def scan(path, framework):
    """Scan Infrastructure-as-Code files for security vulnerabilities."""
    click.echo(f"Scanning path: {path} ...")
    try:
        reports = run_checkov_scan(path, framework=framework)
    except Exception as e:
        click.secho(f"Error executing scan: {e}", fg="red", err=True)
        raise click.Abort()

    if not reports:
        click.echo("No scan reports generated.")
        return

    for report in reports:
        click.echo("")
        click.secho(f"=== Framework: {report.check_type.upper()} ===", fg="cyan", bold=True)
        click.echo(f"Passed: {report.summary.passed} | Failed: {report.summary.failed} | Skipped: {report.summary.skipped}")
        
        failed_findings = [f for f in report.findings if f.check_result == "FAILED"]
        if failed_findings:
            click.secho(f"\nDiscovered {len(failed_findings)} failed checks:", fg="yellow", bold=True)
            for idx, finding in enumerate(failed_findings, 1):
                click.echo(f"\n[{idx}] {finding.check_id}: {finding.check_name}")
                click.echo(f"    Resource: {finding.resource}")
                click.echo(f"    Location: {finding.file_path} (Lines {finding.file_line_range})")
                if finding.guideline:
                    click.echo(f"    Guideline: {finding.guideline}")
        else:
            click.secho("\nNo failed checks found!", fg="green")

if __name__ == "__main__":
    main()
