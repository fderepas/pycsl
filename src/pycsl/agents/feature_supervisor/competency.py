from __future__ import annotations
import argparse, datetime, json, os, re, subprocess, sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from ._common import *

__all__ = [
    '_load_competency_matrix',
    '_phase_level',
    '_phase_role',
    '_phase_competency_skills',
    '_append_resolved_competencies',
]

def _load_competency_matrix() -> Dict[str, List[str]]:
    """Parse the competency matrix's fenced block → {level_key: [skill names]}.

    Keys are `*` (all levels) or `L1`–`L5`; values are `config/skills/<name>`
    directory names. Returns {} if the file/block is absent.
    """
    matrix: Dict[str, List[str]] = {}
    if not _COMPETENCY_FILE.is_file():
        return matrix
    text = _COMPETENCY_FILE.read_text()
    # The machine block is the fenced ``` … ``` containing `key: a, b` lines.
    # Keys are `*`, `L<n>`, or `L<n>-<Role>` (e.g. `L5-Validator`).
    _key = r"(\*|L\d(?:-[A-Za-z][A-Za-z-]*)?)"
    for block in re.findall(r"```\n(.*?)\n```", text, re.S):
        if not re.search(rf"^\s*{_key}\s*:", block, re.M):
            continue
        for line in block.splitlines():
            m = re.match(rf"^\s*{_key}\s*:\s*(.+?)\s*$", line)
            if m:
                skills = [s.strip() for s in m.group(2).split(",") if s.strip()]
                matrix[m.group(1)] = skills
    return matrix


def _phase_level(phase: "Phase") -> str:
    """The phase's `**Level:** L<n>` tag (line-leading), or '' if none."""
    m = re.search(r"^\*\*Level:\*\*\s*(L\d)\b", phase.raw_body, re.M)
    return m.group(1) if m else ""


def _phase_role(phase: "Phase") -> str:
    """The phase's `**Role:** <Role>` tag (e.g. Validator), or '' if none."""
    m = re.search(r"^\*\*Role:\*\*\s*([A-Za-z][A-Za-z-]*)", phase.raw_body, re.M)
    return m.group(1) if m else ""


def _phase_competency_skills(phase: "Phase",
                             matrix: Dict[str, List[str]]) -> List[str]:
    """Skill names this phase needs: union of the `*` row, the phase's level
    row, and (if a role is tagged) the `L<n>-<Role>` row. Deduped, stable
    order. The role combination is how proof skills (`rocq`/`lean`) reach the
    low-level Validator only."""
    level = _phase_level(phase)
    role = _phase_role(phase)
    keys = ["*"]
    if level:
        keys.append(level)
        if role:
            keys.append(f"{level}-{role}")
    out: List[str] = []
    for key in keys:
        for s in matrix.get(key, []):
            if s not in out:
                out.append(s)
    return out


def _append_resolved_competencies(phases: List["Phase"]) -> None:
    """Append `### 5.1 Resolved per-phase competencies` to the harness-structure
    log (path in $PYCSL_HARNESS_LOG) so a human can review which skills each
    phase's delegate will receive. No-op if the env var / log is absent."""
    log_path = os.environ.get("PYCSL_HARNESS_LOG")
    if not log_path:
        return
    matrix = _load_competency_matrix()
    lines = [
        "", "### 5.1 Resolved per-phase competencies",
        "", "From `config/skills/project-lifecycle/references/competency-matrix.md` "
        "(`**Level:**` tag → skills injected into that phase's delegate prompt):", "",
    ]
    for p in phases:
        lvl = _phase_level(p) or "—"
        role = _phase_role(p)
        tag = f"level {lvl}" + (f", role {role}" if role else "")
        skills = _phase_competency_skills(p, matrix)
        skills_str = ", ".join(f"`{s}`" for s in skills) if skills else "(none)"
        lines.append(f"- **Phase {p.number}** ({tag}): {skills_str}")
    lines.append("")
    try:
        with open(log_path, "a") as f:
            f.write("\n".join(lines))
    except OSError:
        pass


