"""Select which theorems become contracts for a given function.

Selection precedence per rocq2pycsl-plan.md §6:

  1. Explicit `spec_theorems` list in the per-function TOML section
     (highest priority — recommended default).
  2. In-source `(* @pycsl-spec <funcname> *)` markers above a theorem
     (medium priority — useful when contracts and proofs evolve together).
  3. Heuristic on function-symbol mention (fallback — must be opt-in
     because mathlib-style proofs sweep in too many helper lemmas).

Heuristic mode is **off by default**; pass `allow_heuristic=True` to
enable. When enabled, it scans theorem statements for `GApp` /
`GVar` nodes whose head matches `func.name`.

In-source markers are parsed from the *original* `.v` source (the comment
stripper would otherwise erase them). The selector takes both the
GallinaModule and the raw text and reconciles them by line number.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from .gallina import (
    GApp,
    GBinOp,
    GDivides,
    GExists,
    GFunctionDef,
    GForall,
    GTheorem,
    GUnaryOp,
    GVar,
    GallinaModule,
    GallinaNode,
)


# Regex matches `(* @pycsl-spec <funcname> *)`, possibly with multiple
# whitespace forms. The body is one identifier (Coq-style).
_MARKER_RE = re.compile(
    r"\(\*\s*@pycsl-spec\s+([A-Za-z_][A-Za-z_0-9']*)\s*\*\)"
)


@dataclass(frozen=True)
class SelectionResult:
    """What the selector decided for one function."""
    func: GFunctionDef
    theorems: tuple[GTheorem, ...]
    # The rule that picked these theorems. Useful for `--verbose` output
    # so users can see whether they got "explicit", "marker", or "heuristic".
    rule: str


def select(
    module: GallinaModule,
    func: GFunctionDef,
    *,
    explicit: Iterable[str] | None = None,
    raw_source: str = "",
    allow_heuristic: bool = False,
) -> SelectionResult:
    """Return the theorems chosen as contracts for `func`.

    Tries each rule in priority order; the first to yield a non-empty
    selection wins. Returns an empty `theorems` tuple if no rule fires
    (the caller decides whether to error out).
    """
    # Rule 1 — explicit TOML list.
    if explicit is not None:
        names = list(explicit)
        if names:
            theorems = _resolve_names(module, names)
            return SelectionResult(func=func, theorems=theorems, rule="explicit")

    # Rule 2 — in-source markers.
    marker_names = _markers_for(raw_source, func.name)
    if marker_names:
        theorems = _resolve_names(module, marker_names)
        return SelectionResult(func=func, theorems=theorems, rule="marker")

    # Rule 3 — heuristic (opt-in).
    if allow_heuristic:
        theorems = tuple(
            t for t in module.theorems if _mentions(t.statement, func.name)
        )
        if theorems:
            return SelectionResult(
                func=func, theorems=theorems, rule="heuristic"
            )

    return SelectionResult(func=func, theorems=(), rule="none")


def _resolve_names(
    module: GallinaModule, names: Iterable[str]
) -> tuple[GTheorem, ...]:
    """Resolve theorem names to GTheorem objects, raising on missing."""
    out: list[GTheorem] = []
    for n in names:
        t = module.theorem(n)
        if t is None:
            raise KeyError(
                f"theorem {n!r} not found in {module.source_path or '<module>'}"
            )
        out.append(t)
    return tuple(out)


def _markers_for(source: str, func_name: str) -> list[str]:
    """Scan `source` for `(* @pycsl-spec <func_name> *)` markers.

    Each marker associates the *next* theorem declaration with
    `func_name`. We pair markers with theorem names by source order.
    Returns the list of theorem names tagged with this function.
    """
    if not source:
        return []
    out: list[str] = []
    # Walk through the source, alternating between markers and Theorem-
    # head matches. A marker followed eventually by a Theorem head
    # claims that theorem.
    cursor = 0
    while True:
        marker = _MARKER_RE.search(source, cursor)
        if marker is None:
            break
        tagged_func = marker.group(1)
        # Look for the next Theorem/Lemma/etc. after this marker.
        thm_match = re.search(
            r"(?:Theorem|Lemma|Proposition|Corollary|Fact|Remark)\s+"
            r"([A-Za-z_][A-Za-z_0-9']*)",
            source[marker.end():],
        )
        if thm_match is None:
            break
        if tagged_func == func_name:
            out.append(thm_match.group(1))
        cursor = marker.end() + thm_match.end()
    return out


def _mentions(node: GallinaNode, func_name: str) -> bool:
    """Recursively check whether `node` mentions `func_name`."""
    if isinstance(node, GVar):
        return node.name == func_name
    if isinstance(node, GApp):
        if node.fn == func_name:
            return True
        return any(_mentions(a, func_name) for a in node.args)
    if isinstance(node, GBinOp):
        return _mentions(node.lhs, func_name) or _mentions(node.rhs, func_name)
    if isinstance(node, GUnaryOp):
        return _mentions(node.arg, func_name)
    if isinstance(node, GForall) or isinstance(node, GExists):
        return _mentions(node.body, func_name)
    if isinstance(node, GDivides):
        return _mentions(node.d, func_name) or _mentions(node.n, func_name)
    return False
