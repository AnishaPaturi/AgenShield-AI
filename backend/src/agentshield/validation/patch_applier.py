"""Patch Applier and Rollback Engine for AgentShield AI.

Applies PatchDiff objects to IaC file contents with tolerance for line-ending
differences and trailing whitespace, and provides atomic rollback capability.
"""

from __future__ import annotations

import logging
from agentshield.core.schemas import PatchDiff

logger = logging.getLogger("agentshield.validation.patch_applier")


def apply_patch_to_content(content: str, patch: PatchDiff) -> tuple[str, bool]:
    """Apply a PatchDiff to the target content.

    Returns:
        tuple[str, bool]: (patched_content, success)
    """
    if not patch.original_code or not patch.patched_code:
        return content, False

    # 1. Exact match attempt
    if patch.original_code in content:
        return content.replace(patch.original_code, patch.patched_code, 1), True

    # 2. Normalized CRLF/LF match
    norm_content = content.replace("\r\n", "\n")
    norm_orig = patch.original_code.replace("\r\n", "\n")
    norm_patched = patch.patched_code.replace("\r\n", "\n")

    if norm_orig in norm_content:
        patched = norm_content.replace(norm_orig, norm_patched, 1)
        if "\r\n" in content:
            patched = patched.replace("\n", "\r\n")
        return patched, True

    # 3. Line-by-line whitespace-insensitive slice matching
    content_lines = norm_content.splitlines(keepends=True)
    orig_lines = norm_orig.splitlines(keepends=True)
    m = len(orig_lines)
    n = len(content_lines)

    if m > 0 and n >= m:
        orig_stripped = [line.rstrip() for line in orig_lines]
        for i in range(n - m + 1):
            window = [content_lines[i + j].rstrip() for j in range(m)]
            if window == orig_stripped:
                # Matched window
                prefix = "".join(content_lines[:i])
                suffix = "".join(content_lines[i + m :])
                patched = prefix + norm_patched + ("\n" if not norm_patched.endswith("\n") and suffix else "") + suffix
                if "\r\n" in content:
                    patched = patched.replace("\n", "\r\n")
                return patched, True

    logger.warning("Could not locate original_code snippet in content for patch_id=%s", patch.patch_id)
    return content, False


def rollback_patch_from_content(content: str, patch: PatchDiff) -> str:
    """Roll back a previously applied PatchDiff, reverting candidate changes."""
    if not patch.original_code or not patch.patched_code:
        return content

    if patch.patched_code in content:
        return content.replace(patch.patched_code, patch.original_code, 1)

    norm_content = content.replace("\r\n", "\n")
    norm_orig = patch.original_code.replace("\r\n", "\n")
    norm_patched = patch.patched_code.replace("\r\n", "\n")

    if norm_patched in norm_content:
        reverted = norm_content.replace(norm_patched, norm_orig, 1)
        if "\r\n" in content:
            reverted = reverted.replace("\n", "\r\n")
        return reverted

    return content
