import click

@click.group()
def main():
    """AgentShield AI - Multi-Agent Framework for Infrastructure-as-Code Security"""
    pass

@main.command()
@click.option('--path', '-p', required=True, type=click.Path(exists=True), help='Path to IaC files or directory to scan')
def scan(path):
    """Scan Infrastructure-as-Code files for security vulnerabilities."""
    click.echo(f"Scanning path: {path} ...")
    # In future phases, this will trigger the ingestion parsers and static checkov scans.

if __name__ == "__main__":
    main()
