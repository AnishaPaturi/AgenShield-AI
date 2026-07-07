from click.testing import CliRunner
from agentshield.cli import main

def test_cli_scan_missing_path():
    runner = CliRunner()
    result = runner.invoke(main, ["scan"])
    assert result.exit_code != 0
    assert "Error: Missing option" in result.output

def test_cli_scan_with_path(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["scan", "--path", str(tmp_path)])
    assert result.exit_code == 0
    assert "Scanning path:" in result.output
