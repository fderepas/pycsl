"""Pretty-print a disagreement.

Matches the layout in pycsl-bridge-plan.md §3.4 — line-by-line diff
of the canonical multisets, with theorem source attribution and a
suggested resolution hint.
"""

from __future__ import annotations

from pycsl_emit.translator import render

from .pipeline import QualnameResult, Status


def format_disagreement(r: QualnameResult) -> str:
    """Render a single disagreement as a multi-line report.

    Only meaningful when `r.status is Status.DISAGREEMENT` — for other
    statuses, a short single-line note is produced.
    """
    if r.status is Status.RECONCILED:
        return f"RECONCILED {r.qualname}: contracts match"
    if r.status is Status.ROCQ_ONLY:
        return (
            f"ROCQ-ONLY {r.qualname}: no @[pycsl_spec \"{r.qualname}\"] "
            f"theorems in the Lean source"
        )
    if r.status is Status.LEAN_ONLY:
        return (
            f"LEAN-ONLY {r.qualname}: no `spec_theorems` listed for this "
            f"function in the rocq2pycsl config"
        )

    assert r.status is Status.DISAGREEMENT
    rocq_theorems = ", ".join(r.rocq["theorems"]) if r.rocq else "<none>"
    lean_theorems = ", ".join(r.lean["theorems"]) if r.lean else "<none>"
    lines = [
        f"DISAGREEMENT: {r.qualname}",
        "",
        f"  Rocq theorems: {rocq_theorems}",
        f"  Lean theorems: {lean_theorems}",
        "",
    ]
    if r.rocq_only_clauses:
        lines.append("  Rocq has clauses not present in Lean (canonical form):")
        for c in r.rocq_only_clauses:
            lines.append(f"    +rocq   {render(c)}")
        lines.append("")
    if r.lean_only_clauses:
        lines.append("  Lean has clauses not present in Rocq (canonical form):")
        for c in r.lean_only_clauses:
            lines.append(f"    +lean   {render(c)}")
        lines.append("")
    lines.extend([
        "  Suggested resolutions:",
        "    - Prove the missing clause(s) in the lagging formalism, OR",
        "    - Remove the extra clause(s) from the leading formalism if not",
        "      intended to be part of the spec.",
    ])
    return "\n".join(lines)
