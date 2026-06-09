"""core_ir_semantic.py — the language-agnostic IR semantic-check seam.

This is the core's *semantic-analysis on the IR* step (spec §6.2; refactor.md
Phase B), distinct from ``ir_schema.validate_ir`` (which does structural/shape
validation, §6.1). It runs after the IR is ingested and validated, makes **no**
reference to any source language, and is the **migration target** for the
language-agnostic logic checks formerly entangled with the Python AST in
Module 4. Each such check moves here one at a time (refactor.md B2..Bn), each
gated by an unchanged full-corpus pass/fail **and** error-message diff.

Because the IR carries source spans (§4.4 — ``line``/``col`` on each function),
a check raised here reports against the original source line in *any*
front-end's language, exactly as an AST-based Module 4 check did.

Migrated so far:
  - B1: the §4.4 front-end span contract (every function carries a span).
  - B2: ``no_exception`` well-formedness (was Module 4 ``_validate_no_exception``).
  - B3: ``assigns``-region base typing (was Module 4 ``_validate_assigns_regions``).
  - B4: predicate bases — ``\\length`` not on dict/set, ``\\valid``/``\\separated``
        bases must be list/bytes (was Module 4 ``_validate_predicate_bases``). This
        one is a *surface-tracking* expr-walker: the error context varies by where
        the predicate sits — function contract, while-loop invariant (with the
        innermost loop's line), or ghost expression (simple / subscript).
"""
from __future__ import annotations

from typing import Any

from errors import PyCSLSemanticError


def run_ir_semantic_checks(ir: Any, *, stage: str = "ir-semantic") -> None:
    """Run the language-agnostic semantic checks on the IR (read-only, in place)."""
    for func in ir.get("functions", []):
        _check_span(func, stage)
        _check_no_exception(func)
        _check_assigns_regions(func)
        _check_predicate_bases(func)


def _check_span(func: Any, stage: str) -> None:
    """§4.4 front-end contract: every function carries a source span, so any
    migrated check can locate its error. Holds by construction for the Python
    front-end (Module 5 stamps ``line``/``col``); catches a non-conforming one."""
    if "line" not in func:
        name = func.get("name", "<anonymous>")
        raise PyCSLSemanticError(
            f"IR function '{name}' carries no source span; a front-end must "
            f"stamp §4.4 spans (line/col) on every node",
            stage=stage,
        )


def _check_no_exception(func: Any) -> None:
    """B2 — ``no_exception`` well-formedness, migrated verbatim from Module 4's
    ``_validate_no_exception`` (which ran on the AST). Pure contract data, all
    present in the IR: ``no_exception`` (names), ``no_exception_all``, and
    ``raises[].exc_type``. Reports with the IR's name + §4.4 span, reproducing
    Module 4's messages exactly (no ``stage`` prefix — matching the original raise):

      - a ``no_exception`` name must be a known exception;
      - ``no_exception E`` and ``raises { E -> _ }`` for the same E is contradictory;
      - ``no_exception \\all`` with any ``raises`` clause is rejected.
    """
    from exception_model import KNOWN_EXCEPTIONS  # lazy: keep the import surface small

    contracts = func.get("contracts") or {}
    no_exc = list(contracts.get("no_exception", []) or [])
    no_exc_all = bool(contracts.get("no_exception_all", False))
    raises = contracts.get("raises", []) or []
    raised_names = {r.get("exc_type") for r in raises}

    where = f"function '{func.get('name', '<anonymous>')}' (line {func.get('line', 0)})"

    for name in no_exc:
        if name not in KNOWN_EXCEPTIONS:
            raise PyCSLSemanticError(
                f"{where}: no_exception names unknown exception '{name}'. "
                f"Known: {sorted(KNOWN_EXCEPTIONS)}."
            )
        if name in raised_names:
            raise PyCSLSemanticError(
                f"{where}: contradictory annotations — no_exception {name} "
                f"and raises {{ {name} -> ... }} cannot both apply."
            )
    if no_exc_all and raised_names:
        raise PyCSLSemanticError(
            f"{where}: no_exception \\all requires the raises set to be empty; "
            f"found raises {{ {', '.join(sorted(raised_names))} -> ... }}."
        )


def _check_assigns_regions(func: Any) -> None:
    """B3 — `assigns`-region bases must be list-typed variables in scope, migrated
    verbatim from Module 4's ``_validate_assigns_regions`` (which ran on the AST).
    The IR carries the assigns targets (each an ``{"type": "AssignsRegion",
    "base": ...}`` node) and the ``symbol_table`` (var → type), so the check runs
    on the IR alone and reports with the IR function name.

    (The undefined-base path is in practice shadowed by the general contract-scope
    check that still runs in Module 4 — kept here for fidelity to the original.)
    """
    where = f"function '{func.get('name', '<anonymous>')}'"
    symtab = func.get("symbol_table") or {}
    for target in func.get("contracts", {}).get("assigns", []) or []:
        if isinstance(target, dict) and target.get("type") == "AssignsRegion":
            base = target.get("base")
            arr_type = symtab.get(base)
            if arr_type is None:
                raise PyCSLSemanticError(
                    f"Assigns region references undefined variable '{base}' in {where}."
                )
            if arr_type not in ("list", "List", "Any"):
                raise PyCSLSemanticError(
                    f"Assigns region on non-list variable '{base}' "
                    f"(type '{arr_type}') in {where}."
                )


# --- B4: predicate bases (surface-tracking expr-walker) ----------------------

_PB_ARRAY_BASE_TYPES = ("list", "List", "bytes", "bytearray", "Any", None)
_PB_LENGTHLESS_TYPES = ("dict", "Dict", "set", "Set", "frozenset", "FrozenSet")


def _check_predicate_bases(func) -> None:
    """B4 — `\\length` not on a dict/set, and `\\valid`/`\\separated` bases must be
    list/bytes, migrated from Module 4's ``_validate_predicate_bases``. Unlike the
    flat-metadata checks (B2/B3), this walks the contract EXPRESSION trees, and the
    error context depends on the predicate's *surface* — which Module 4 reproduced
    from its AST visitor and the core now reconstructs from the IR:
      - function contracts (requires/ensures/assigns/variants) → ``function 'F'``;
      - WHILE-loop invariants/variants → ``while loop at line N inside function 'F'``
        (innermost enclosing while; for-loop invariants are NOT checked, matching
        Module 4 — it has no for-loop visitor for this);
      - ghost values → ``function 'F' (ghost 'g')`` (simple) /
        ``function 'F' (ghost 'g[...]')`` (subscript, GhostArraySet).
    Gated by drivers 0667–0673 staying XFAIL with byte-identical messages.
    """
    fname = func.get("name", "<anonymous>")
    symtab = func.get("symbol_table") or {}
    fctx = f"function '{fname}'"
    contracts = func.get("contracts") or {}
    for key in ("requires", "ensures", "assigns", "function_variants"):
        for clause in contracts.get(key, []) or []:
            _pb_expr(clause, fctx, symtab)
    _pb_body(func.get("body", []) or [], fname, symtab)


def _pb_body(stmts, fname, symtab) -> None:
    """Walk a statement list, applying the predicate checks to while-invariants and
    ghost values with their surface-specific context, recursing into nested bodies."""
    for s in stmts:
        if isinstance(s, dict):
            _pb_stmt(s, fname, symtab)


def _pb_stmt(s, fname, symtab) -> None:
    st = s.get("stmt")
    if st == "While":
        lctx = f"while loop at line {s.get('line', 0)} inside function '{fname}'"
        for clause in (s.get("invariants") or []):
            _pb_expr(clause, lctx, symtab)
        for clause in (s.get("variants") or []):
            _pb_expr(clause, lctx, symtab)
        _pb_body(s.get("body", []) or [], fname, symtab)
    elif st == "For":
        # Module 4 does NOT validate for-loop invariants (no for-loop visitor for
        # this check) — recurse the body only, do not touch the invariants.
        _pb_body(s.get("body", []) or [], fname, symtab)
    elif st == "GhostAssign":
        _pb_expr(s.get("value"),
                 f"function '{fname}' (ghost '{s.get('target')}')", symtab)
    elif st == "GhostArraySet":
        gctx = f"function '{fname}' (ghost '{s.get('target')}[...]')"
        _pb_expr(s.get("index"), gctx, symtab)
        _pb_expr(s.get("value"), gctx, symtab)
    else:
        # Other compound statements (If/Match/Try/With/…): descend into nested
        # statement lists to find deeper whiles / ghosts.
        for v in s.values():
            _pb_descend(v, fname, symtab)


def _pb_descend(v, fname, symtab) -> None:
    if isinstance(v, dict):
        if "stmt" in v:
            _pb_stmt(v, fname, symtab)
        else:
            for x in v.values():
                _pb_descend(x, fname, symtab)
    elif isinstance(v, list):
        for x in v:
            _pb_descend(x, fname, symtab)


def _pb_expr(node, ctx, symtab) -> None:
    """Recursively check `\\length`/`\\valid`/`\\separated` nodes in a contract-expr
    tree, reporting against the surface context. Messages reproduce Module 4 verbatim."""
    if isinstance(node, list):
        for x in node:
            _pb_expr(x, ctx, symtab)
        return
    if not isinstance(node, dict):
        return
    t = node.get("type")
    if t == "ArrayLen":
        var = node.get("var", "")
        if not str(var).startswith("self.") and var != "\\result":
            typ = symtab.get(var)
            if typ in _PB_LENGTHLESS_TYPES:
                raise PyCSLSemanticError(
                    f"\\length is not supported on the {typ}-typed '{var}' in "
                    f"{ctx}: dicts/sets are modelled as total maps "
                    f"(`map int (option int)`) with no cardinality. Use \\has_key(d, k) "
                    f"for key presence, or a list/array for a length-bearing collection."
                )
    elif t == "Valid":
        base = node.get("base")
        arr_type = symtab.get(base)
        if arr_type not in _PB_ARRAY_BASE_TYPES:
            raise PyCSLSemanticError(
                f"\\valid base '{base}' is not a list/bytes parameter "
                f"in {ctx} (got type '{arr_type}')."
            )
    elif t == "Separated":
        for base in (node.get("base1"), node.get("base2")):
            arr_type = symtab.get(base)
            if arr_type not in _PB_ARRAY_BASE_TYPES:
                raise PyCSLSemanticError(
                    f"\\separated base '{base}' is not a list/bytes parameter "
                    f"in {ctx} (got type '{arr_type}')."
                )
    for v in node.values():
        _pb_expr(v, ctx, symtab)
