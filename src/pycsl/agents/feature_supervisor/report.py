from __future__ import annotations
import argparse, datetime, json, os, re, subprocess, sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from ._common import *

__all__ = [
    'write_halt_report',
    '_print_halt',
]

def write_halt_report(
    feature_file: Path,
    phases: List[Phase],
    deny_hits: List[Tuple[int, str, str]],
    gate_results: List[GateResult],
    exit_reason: str,
    acceptance_failures: Optional[List[Tuple["Phase", "AcceptanceResult"]]] = None,
    missing_acceptance_phases: Optional[List["Phase"]] = None,
    explanation: Optional[str] = None,
) -> Path:
    slug = _slug(feature_file.stem)
    report_dir = _HALT_REPORT_ROOT / slug
    report_dir.mkdir(parents=True, exist_ok=True)
    out = report_dir / "halt-report.md"
    ts = (
        datetime.datetime.now(datetime.UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
    lines: List[str] = [
        f"# agent-feature-supervisor halt report — {slug}",
        "",
        f"**Generated:** {ts}",
        f"**Feature file:** `{feature_file}`",
        f"**Reason:** {exit_reason}",
        "",
    ]
    # Plain-English explanation of what happened, in addition to the
    # machine reason code, so the report is readable without tracing code.
    if explanation:
        lines += ["## What this means", "", explanation, ""]
    lines += [
        "## Parsed phases",
        "",
    ]
    for p in phases:
        lines.append(f"### Phase {p.number} — {p.title}")
        lines.append("")
        lines.append(f"**Target files ({len(p.target_files)}):**")
        for t in p.target_files:
            tag = ""
            for ph_num, target, matched in deny_hits:
                if ph_num == p.number and target == t:
                    tag = f"  ← **LOAD-BEARING** (matches `{matched}`)"
                    break
            lines.append(f"- `{t}`{tag}")
        lines.append("")

    if deny_hits:
        lines += [
            "## Load-bearing deny-list hits",
            "",
            "These target files appear in the deny-list at "
            "`config/skills/agent-stdlib-annotate/references/load-bearing-files.md`. "
            "Per the safety perimeter (better-agent.md §Safety perimeter), the "
            "supervisor halts and requires human review before any edit attempt.",
            "",
        ]
        for ph_num, target, matched in deny_hits:
            lines.append(
                f"- Phase {ph_num}: `{target}` matches deny-list entry `{matched}`"
            )
        lines.append("")

    if gate_results:
        lines += ["## Verification gate", ""]
        for r in gate_results:
            mark = "SKIP" if r.skipped else ("PASS" if r.passed else "FAIL")
            lines.append(f"- [{mark}] {r.step}")
            if not r.passed and not r.skipped:
                lines.append("")
                lines.append("  ```")
                for ln in r.output.splitlines()[-10:]:
                    lines.append(f"  {ln}")
                lines.append("  ```")
        lines.append("")

    # ER: missing-acceptance phases
    if missing_acceptance_phases:
        lines += [
            "## Missing Acceptance blocks",
            "",
            "These phases carry neither `**Status:** DONE` nor an "
            "`**Acceptance:**` block. Per Extreme Rigor (see "
            "`feature-supervisor-extreme-rigor.md`), every open phase "
            "must declare machine-checkable acceptance claims so the "
            "supervisor can evaluate \"done\" without asking the human "
            "*what was not done*.",
            "",
        ]
        for p in missing_acceptance_phases:
            lines.append(f"- Phase {p.number} — {p.title}")
        lines.append("")
        lines += [
            "To resolve, add an `**Acceptance:**` block to each phase. "
            "If the phase is intentionally not machine-checkable, use "
            "`**Acceptance:** none — <reason>` to opt out explicitly.",
            "",
        ]

    # ER: acceptance failures (including CLAIM_REJECTED)
    if acceptance_failures:
        lines += ["## Acceptance failures", ""]
        for p, res in acceptance_failures:
            status_tag = "DONE → STATUS_FORGED" if p.status_done else "open"
            lines.append(
                f"### Phase {p.number} — {p.title} ({status_tag})"
            )
            lines.append("")
            lines.append(f"- Claim: `{res.claim.raw_line}`")
            lines.append(f"  - Command: `{res.claim.command}`")
            lines.append(f"  - Predicate: {res.claim.predicate.describe()}")
            lines.append(f"  - Outcome: {res.reason_if_failed}")
            if res.stdout_excerpt:
                lines.append("  - Stdout (last 500 chars):")
                lines.append("    ```")
                for ln in res.stdout_excerpt.splitlines():
                    lines.append(f"    {ln}")
                lines.append("    ```")
            lines.append("")

    lines += [
        "## Next steps",
        "",
        "1. Human reviews the deny-list hits and decides whether to "
        "proceed with manual edits or to reject the plan.",
        "2. After manual edits, re-run `bin/cmmi-audit.sh` to confirm "
        "the gate is green.",
        "3. If the plan needs revision, edit the feature file and "
        "re-invoke `bin/agent-feature-supervisor --feature-file <path>`.",
        "",
    ]
    out.write_text("\n".join(lines))
    return out


def _print_halt(out: Path, exit_reason: str, exit_code: int,
                explanation: str,
                review: Optional[List[Tuple[str, Path]]] = None) -> None:
    """Print an explicit, human-readable halt summary to the terminal.

    Beyond the machine reason code, this emits (1) a short plain-English
    paragraph saying what happened and what to do, and (2) the ABSOLUTE
    path of the halt-report (plus any other files worth opening), so the
    operator knows exactly where to look without rebuilding relative
    paths. Mirrors the report's `## What this means` section.
    """
    code = exit_reason.split(":", 1)[0].strip()
    print(f"[{AGENT_NAME}] HALT — {code} (exit {exit_code})")
    for ln in explanation.splitlines():
        if ln.strip():
            print(f"[{AGENT_NAME}]   {ln.rstrip()}")
    print(f"[{AGENT_NAME}]   review:")
    print(f"[{AGENT_NAME}]     halt-report : {out.resolve()}")
    for label, path in (review or []):
        print(f"[{AGENT_NAME}]     {label:<11}: {Path(path).resolve()}")


# ---------------------------------------------------------------------------
# Main loop (v1 — gate-only)
# ---------------------------------------------------------------------------

