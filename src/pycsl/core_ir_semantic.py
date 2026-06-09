"""core_ir_semantic.py — the language-agnostic IR semantic-check seam.

This is the core's *semantic-analysis on the IR* step (spec §6.2; refactor.md
Phase B), distinct from ``ir_schema.validate_ir`` (which does structural/shape
validation, §6.1). It runs after the IR is ingested and validated, makes **no**
reference to any source language, and is the **migration target** for the
language-agnostic logic checks currently entangled with the Python AST in
Module 4 — the forbidden-expression rules, datatype/positivity checks, frame
(``assigns``) consistency, ``\\variant``-for-recursion, behavior-block coverage,
and so on. Each such check moves here one at a time (refactor.md B2..Bn), each
gated by an unchanged full-corpus pass/fail **and** error-message diff.

Because the IR carries source spans (§4.4 — ``line``/``col`` on each function),
a check raised here reports against the original source line in *any*
front-end's language, exactly as an AST-based Module 4 check does today.
"""
from __future__ import annotations

from typing import Any

from errors import PyCSLSemanticError


def run_ir_semantic_checks(ir: Any, *, stage: str = "ir-semantic") -> None:
    """Run the language-agnostic semantic checks on the IR (read-only, in place).

    The seam Module 4's language-agnostic checks migrate into (refactor.md B2..Bn).
    It currently enforces the §4.4 **front-end contract**: every function carries
    a source span, so any migrated check can locate its error. This holds by
    construction for the Python front-end (Module 5 stamps ``line``/``col``); the
    check exists to catch a *non-conforming* front-end rather than to fire on the
    corpus.
    """
    for func in ir.get("functions", []):
        if "line" not in func:
            name = func.get("name", "<anonymous>")
            raise PyCSLSemanticError(
                f"IR function '{name}' carries no source span; a front-end must "
                f"stamp §4.4 spans (line/col) on every node",
                stage=stage,
            )
