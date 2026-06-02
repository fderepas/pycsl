from __future__ import annotations
import argparse, datetime, json, os, re, subprocess, sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from ._common import *
from .acceptance import *

__all__ = [
    'Phase',
    '_PHASE_HEADER_RE',
    '_PATH_RE',
    'parse_feature_plan',
]

@dataclass
class Phase:
    number: int
    title: str
    target_files: List[str] = field(default_factory=list)
    raw_body: str = ""
    status_done: bool = False
    acceptance: List[AcceptanceClaim] = field(default_factory=list)
    optout_reason: Optional[str] = None   # set when `Acceptance: none — …`
    has_acceptance_header: bool = False


_PHASE_HEADER_RE = re.compile(
    r"^###\s+Phase\s+(\d+)\s*(?:\.\d+)?\s*(?:—|-|:|\b)?\s*(.*?)\s*$",
    re.M,
)

# File references inside phase tables — match `path/like/this.py`
# (with or without backticks). We accept paths that contain a `/`
# or end in a recognised extension to avoid matching English words.
_PATH_RE = re.compile(
    r"`([^`\n]+?\.[A-Za-z0-9]+|[^`\n]+?/[^`\n]+?)`"
)


def parse_feature_plan(text: str) -> List[Phase]:
    """Extract the phase list from a missing-*-feature.md document.

    Under Extreme Rigor, phases are NO LONGER skipped wholesale when
    they carry `**Status:** DONE` — they're tracked with
    `status_done=True` so the supervisor can verify their acceptance
    claims still pass (STATUS_FORGED check). DONE phases without an
    Acceptance block are treated as `LEGACY_ACCEPTED` (informational).

    For purposes of deny-list classification, DONE phases' target
    files are still ignored (they represent completed work whose
    load-bearing references should not re-trigger deny-list halts).
    """
    section_match = re.search(
        r"^##\s+Implementation surface\b(.*?)(?=^##\s+(?!#))",
        text, re.S | re.M,
    )
    body = section_match.group(1) if section_match else text

    headers = list(_PHASE_HEADER_RE.finditer(body))
    phases: List[Phase] = []
    for i, m in enumerate(headers):
        start = m.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(body)
        phase_body = body[start:end]
        # Anchor to start of line so prose mentions of `**Status:**
        # DONE` inside backticked text or table cells don't falsely
        # flag a phase as DONE. Real Status markers are always
        # line-leading.
        status_done = bool(re.search(
            r"^\*\*Status:\*\*\s+DONE\b", phase_body, re.I | re.M))
        # Target-file scan: skip for DONE phases (their load-bearing
        # references are historical) and skip if a `## What ER would
        # have caught` retrospective sub-section appears (those quote
        # example acceptance blocks, not real targets).
        targets: List[str] = []
        if not status_done:
            seen = set()
            for pm in _PATH_RE.finditer(phase_body):
                p = pm.group(1).strip()
                if p.startswith(("http://", "https://", "git@")):
                    continue
                if p in seen:
                    continue
                seen.add(p)
                targets.append(p)
        acceptance = _parse_acceptance(phase_body)
        optout = _acceptance_optout_reason(phase_body)
        phases.append(Phase(
            number=int(m.group(1)),
            title=m.group(2).strip(),
            target_files=targets,
            raw_body=phase_body.strip(),
            status_done=status_done,
            acceptance=acceptance,
            optout_reason=optout,
            has_acceptance_header=_has_acceptance_header(phase_body),
        ))
    return phases


# ---------------------------------------------------------------------------
# Extreme Rigor: acceptance executor + safety validator
# ---------------------------------------------------------------------------

# Tokens forbidden in acceptance commands. Acceptance must be
# read-only: no state mutation, no network, no multi-statement
# shell. The supervisor halts with `CLAIM_REJECTED` before running
# any rejected claim.
