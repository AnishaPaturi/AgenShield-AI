"""CLI tool for generating and exporting security reports (Task 4.4)."""

import argparse
import sys
from pathlib import Path

from agentshield.agents.reporter import ReportAgent
from agentshield.api.store import workspace_store


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agentshield.cli.report",
        description="Generate and export audit-ready security compliance reports.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # export command
    p_export = subparsers.add_parser("export", help="Export workspace report to file.")
    p_export.add_argument("workspace_id", help="Workspace UUID to export.")
    p_export.add_argument(
        "--format",
        "-f",
        default="markdown",
        choices=["json", "markdown", "md", "html", "sarif", "pdf"],
        help="Export format (default: markdown)",
    )
    p_export.add_argument(
        "--output",
        "-o",
        default="",
        help="Target output file path. Defaults to report.<format> in current directory.",
    )

    # summary command
    p_summary = subparsers.add_parser("summary", help="Print executive summary for workspace.")
    p_summary.add_argument("workspace_id", help="Workspace UUID.")

    args = parser.parse_args(argv)

    ws = workspace_store.get(args.workspace_id)
    if not ws:
        print(f"Error: Workspace '{args.workspace_id}' not found.", file=sys.stderr)
        return 1

    agent = ReportAgent()

    if args.command == "summary":
        summary = agent.generate_executive_summary(ws)
        print("=== AgentShield AI Executive Security Summary ===")
        for k, v in summary.items():
            print(f"  {k}: {v}")
        return 0

    if args.command == "export":
        fmt = args.format.lower()
        ext = "md" if fmt == "markdown" else fmt
        out_path = args.output or f"agentshield_report_{args.workspace_id[:8]}.{ext}"
        saved_file = agent.save_report_to_file(ws, out_path, export_format=fmt)
        print(f"Report successfully exported ({fmt.upper()}): {saved_file.resolve()}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
