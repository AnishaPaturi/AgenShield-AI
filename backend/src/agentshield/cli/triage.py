"""CLI Triage Interface for Human Security Audit Queue (Task 3.4).

Allows security engineers to inspect, approve, or reject flagged findings
directly from the terminal.

Usage:
    python -m agentshield.cli.triage list [--status PENDING_REVIEW] [--priority HIGH]
    python -m agentshield.cli.triage stats
    python -m agentshield.cli.triage inspect <item_id>
    python -m agentshield.cli.triage approve <item_id> [--reviewer <name>] [--comment <text>]
    python -m agentshield.cli.triage reject <item_id> [--reviewer <name>] [--comment <text>]
    python -m agentshield.cli.triage interactive
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from agentshield.api.store import workspace_store
from agentshield.core.audit import (
    AuditDecision,
    AuditStatus,
    audit_queue_manager,
)


def format_table_row(cols: list[str], widths: list[int]) -> str:
    """Format a row of fixed-width columns."""
    formatted = []
    for col, width in zip(cols, widths):
        val = str(col)
        if len(val) > width:
            val = val[: width - 3] + "..."
        formatted.append(val.ljust(width))
    return " | ".join(formatted)


def cmd_list(args: argparse.Namespace) -> int:
    """List items in the audit queue."""
    status_filter = args.status
    priority_filter = args.priority
    workspace_filter = args.workspace

    items = audit_queue_manager.list_items(
        status=status_filter,
        priority=priority_filter,
        workspace_id=workspace_filter,
    )

    if not items:
        print("\n[+] Audit queue is empty or no items match the given filters.\n")
        return 0

    headers = ["Item ID", "Severity", "Priority", "Conf", "Resource", "Trigger", "Status"]
    widths = [36, 10, 10, 6, 26, 22, 16]

    print("\n" + "=" * 135)
    print("  AGENTSHIELD AI — HUMAN SECURITY AUDIT QUEUE")
    print("=" * 135)
    print(format_table_row(headers, widths))
    print("-" * 135)

    for item in items:
        row = [
            item.item_id,
            item.finding.severity.value,
            item.priority,
            f"{item.finding.confidence_score:.2f}",
            item.finding.affected_resource,
            item.escalation_trigger.value,
            item.status.value,
        ]
        print(format_table_row(row, widths))

    print("-" * 135)
    print(f"Total: {len(items)} item(s) listed.\n")
    return 0


def cmd_stats(_args: argparse.Namespace) -> int:
    """Display audit queue metrics and summary."""
    summary = audit_queue_manager.get_queue_summary()
    print("\n" + "=" * 60)
    print("  AGENTSHIELD AI — AUDIT QUEUE METRICS")
    print("=" * 60)
    print(f"  Total Items:            {summary['total_items']}")
    print(f"  Pending Review:         {summary['pending_count']}")
    print(f"    - Critical Pending:   {summary['critical_pending']}")
    print(f"    - High Pending:       {summary['high_pending']}")
    print(f"  Approved (Remediated):  {summary['approved_count']}")
    print(f"  Rejected (False Pos):   {summary['rejected_count']}")
    print(f"  Average Confidence:     {summary['avg_confidence']:.4f}")
    print("=" * 60 + "\n")
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    """Inspect detailed information about a specific audit queue item."""
    item = audit_queue_manager.get_item(args.item_id)
    if not item:
        print(f"\n[-] Error: Audit item '{args.item_id}' not found.\n", file=sys.stderr)
        return 1

    f = item.finding
    print("\n" + "=" * 80)
    print(f"  AUDIT ITEM: {item.item_id}")
    print("=" * 80)
    print(f"  Status:             {item.status.value}")
    print(f"  Workspace ID:       {item.workspace_id}")
    print(f"  Target File:        {item.file_path}")
    print(f"  Rule ID:            {f.rule_id} — {f.title}")
    print(f"  Severity:           {f.severity.value}")
    print(f"  Priority Level:     {item.priority} (Score: {item.priority_score})")
    print(f"  Confidence Score:   {f.confidence_score:.4f} (Consensus: {f.consensus_score})")
    print(f"  Affected Resource:  {f.affected_resource} ({f.resource_type or 'unknown'})")
    print(f"  Escalation Trigger: {item.escalation_trigger.value}")
    print(f"  Escalation Reason:  {item.escalation_reason}")

    if item.attack_path:
        print(f"\n  Exploitability Route (Attack Path):")
        print(f"    {' → '.join(item.attack_path)}")

    print(f"  Blast Radius:       {item.blast_radius} downstream resource(s)")

    print(f"\n  Description:\n    {f.description}")

    if f.compliance_mappings:
        cm_str = ", ".join(f"{m.framework.value}:{m.control_id}" for m in f.compliance_mappings)
        print(f"\n  Compliance Mappings: {cm_str}")

    if item.suggested_patch and item.suggested_patch.unified_diff:
        print("\n  Suggested Remediation Diff:")
        print("  " + "-" * 76)
        for line in item.suggested_patch.unified_diff.strip().split("\n"):
            print(f"    {line}")
        print("  " + "-" * 76)

    if item.reviewed_at:
        print(f"\n  Triage Decision Details:")
        print(f"    Reviewed By: {item.reviewer}")
        print(f"    Reviewed At: {item.reviewed_at.isoformat()}")
        if item.reviewer_comment:
            print(f"    Comment:     {item.reviewer_comment}")

    print("=" * 80 + "\n")
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    """Approve a queued finding for remediation."""
    try:
        decision = AuditDecision(
            decision="approve",
            reviewer=args.reviewer or "security_engineer",
            comment=args.comment,
        )
        updated = audit_queue_manager.submit_decision(
            args.item_id, decision, workspace_store=workspace_store
        )
        print(f"\n[+] Successfully APPROVED audit item '{updated.item_id}'.")
        print(f"    Finding '{updated.finding.rule_id}' marked auto-patchable.")
        print(f"    Reviewer: {updated.reviewer}\n")
        return 0
    except KeyError:
        print(f"\n[-] Error: Audit item '{args.item_id}' not found.\n", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n[-] Error approving item: {e}\n", file=sys.stderr)
        return 1


def cmd_reject(args: argparse.Namespace) -> int:
    """Reject a queued finding as false positive."""
    try:
        decision = AuditDecision(
            decision="reject",
            reviewer=args.reviewer or "security_engineer",
            comment=args.comment,
        )
        updated = audit_queue_manager.submit_decision(
            args.item_id, decision, workspace_store=workspace_store
        )
        print(f"\n[+] Successfully REJECTED audit item '{updated.item_id}' (marked False Positive).")
        print(f"    Reviewer: {updated.reviewer}\n")
        return 0
    except KeyError:
        print(f"\n[-] Error: Audit item '{args.item_id}' not found.\n", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n[-] Error rejecting item: {e}\n", file=sys.stderr)
        return 1


def cmd_interactive(args: argparse.Namespace) -> int:
    """Interactive CLI review mode to triage pending findings one-by-one."""
    reviewer = args.reviewer or "security_engineer"
    pending = audit_queue_manager.list_items(status=AuditStatus.PENDING_REVIEW)

    if not pending:
        print("\n[+] No pending audit items to triage!\n")
        return 0

    print("\n" + "=" * 70)
    print(f"  ENTERING INTERACTIVE TRIAGE MODE ({len(pending)} pending items)")
    print("=" * 70)

    for idx, item in enumerate(pending, 1):
        f = item.finding
        print(f"\n[{idx}/{len(pending)}] Audit Item: {item.item_id}")
        print(f"Rule:       {f.rule_id} — {f.title}")
        print(f"Severity:   {f.severity.value} | Priority: {item.priority} (Score: {item.priority_score})")
        print(f"Resource:   {f.affected_resource}")
        print(f"Confidence: {f.confidence_score:.4f} | Consensus: {f.consensus_score}")
        print(f"Escalation: {item.escalation_reason}")

        if item.attack_path:
            print(f"Attack Path: {' → '.join(item.attack_path)}")

        if item.suggested_patch and item.suggested_patch.unified_diff:
            print("\nSuggested Diff:")
            for line in item.suggested_patch.unified_diff.strip().split("\n")[:10]:
                print(f"  {line}")

        while True:
            choice = input("\nAction [ (a)pprove / (r)eject / (s)kip / (q)uit ]: ").strip().lower()
            if choice == "a":
                comment = input("Approval comment (optional): ").strip() or None
                audit_queue_manager.submit_decision(
                    item.item_id,
                    AuditDecision(decision="approve", reviewer=reviewer, comment=comment),
                    workspace_store=workspace_store,
                )
                print(f"[+] Approved item {item.item_id}")
                break
            elif choice == "r":
                comment = input("Rejection reason (required): ").strip()
                if not comment:
                    comment = "False positive dismissed by security engineer."
                audit_queue_manager.submit_decision(
                    item.item_id,
                    AuditDecision(decision="reject", reviewer=reviewer, comment=comment),
                    workspace_store=workspace_store,
                )
                print(f"[+] Rejected item {item.item_id}")
                break
            elif choice == "s":
                print("[*] Skipped.")
                break
            elif choice == "q":
                print("\n[*] Exiting interactive triage mode.\n")
                return 0
            else:
                print("Invalid option. Please enter 'a', 'r', 's', or 'q'.")

    print("\n[+] Finished triaging all pending items!\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="agentshield-triage",
        description="AgentShield AI — Human Security Audit Queue & Triage Interface (Task 3.4)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Triage subcommand")

    # list
    p_list = subparsers.add_parser("list", help="List audit items")
    p_list.add_argument("--status", choices=["PENDING_REVIEW", "APPROVED", "REJECTED"], help="Filter by review status")
    p_list.add_argument("--priority", choices=["CRITICAL", "HIGH", "MEDIUM", "LOW"], help="Filter by priority")
    p_list.add_argument("--workspace", help="Filter by workspace ID")

    # stats
    subparsers.add_parser("stats", help="Show queue statistics")

    # inspect
    p_inspect = subparsers.add_parser("inspect", help="Inspect a specific finding")
    p_inspect.add_argument("item_id", help="Audit item ID to inspect")

    # approve
    p_approve = subparsers.add_parser("approve", help="Approve finding for remediation")
    p_approve.add_argument("item_id", help="Audit item ID to approve")
    p_approve.add_argument("--reviewer", default="security_engineer", help="Reviewer identity")
    p_approve.add_argument("--comment", help="Optional approval rationale")

    # reject
    p_reject = subparsers.add_parser("reject", help="Reject finding as false positive")
    p_reject.add_argument("item_id", help="Audit item ID to reject")
    p_reject.add_argument("--reviewer", default="security_engineer", help="Reviewer identity")
    p_reject.add_argument("--comment", help="Rejection explanation")

    # interactive
    p_interactive = subparsers.add_parser("interactive", help="Interactive terminal triage loop")
    p_interactive.add_argument("--reviewer", default="security_engineer", help="Reviewer identity")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    commands = {
        "list": cmd_list,
        "stats": cmd_stats,
        "inspect": cmd_inspect,
        "approve": cmd_approve,
        "reject": cmd_reject,
        "interactive": cmd_interactive,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
