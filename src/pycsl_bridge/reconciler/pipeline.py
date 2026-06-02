"""Reconcile rocq + lean IR-dump envelopes.

Per pycsl-bridge-plan.md §3.3. The pipeline:

  1. Decode both envelopes (via pycsl_emit.ir_dump.decode_envelope).
  2. For every Python qualname in the union of both:
       - Look up the per-side contract entries.
       - Canonicalize all `ensures` (and `requires`) clauses
         independently using `pycsl_bridge.canonicalizer.canonicalize`.
       - Compare as multisets.
  3. Classify the qualname's status:
       - RECONCILED   — both sides present, canonical multisets equal.
       - DISAGREEMENT — both sides present, canonical multisets differ.
       - ROCQ_ONLY    — only the rocq envelope mentions it.
       - LEAN_ONLY    — only the lean envelope mentions it.

The Result carries the *original* (non-canonical) clauses too, so the
caller can pick which side's spelling to emit and so the diff can show
the user the surface form rather than the canonical machinery.
"""

from __future__ import annotations

import enum
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from pycsl_emit.ir import Node
from pycsl_emit.ir_dump import decode_contract_clauses, decode_envelope

from ..canonicalizer import canonicalize


class Status(str, enum.Enum):
    RECONCILED = "reconciled"
    ROCQ_ONLY = "rocq-only"
    LEAN_ONLY = "lean-only"
    DISAGREEMENT = "disagreement"


@dataclass
class QualnameResult:
    """The bridge's verdict for one Python qualname.

    `chosen` contains the contract clauses we emit onto the Python
    source — the rocq or lean entry, depending on which side(s) are
    present. For disagreements we still pick a side (rocq by default)
    so the caller can `--on-disagreement=force` and the output is
    deterministic.
    """
    qualname: str
    status: Status
    rocq: dict[str, Any] | None        # decoded clause dict per ir_dump.decode_contract_clauses
    lean: dict[str, Any] | None
    chosen: dict[str, Any]              # whichever side feeds the emitter
    # On disagreement, the differing clauses (canonical form, both sides):
    rocq_only_clauses: list[Node] = field(default_factory=list)
    lean_only_clauses: list[Node] = field(default_factory=list)


@dataclass
class Reconciliation:
    """End-to-end summary across all qualnames in the two envelopes."""
    results: dict[str, QualnameResult] = field(default_factory=dict)
    rocq_source: str = ""
    lean_source: str = ""

    def by_status(self, status: Status) -> list[QualnameResult]:
        return [r for r in self.results.values() if r.status is status]

    @property
    def disagreements(self) -> list[QualnameResult]:
        return self.by_status(Status.DISAGREEMENT)

    @property
    def reconciled(self) -> list[QualnameResult]:
        return self.by_status(Status.RECONCILED)


def reconcile_envelopes(
    rocq_env: dict[str, Any],
    lean_env: dict[str, Any],
) -> Reconciliation:
    """Top-level entry: decode + canonicalize + compare."""
    decode_envelope(rocq_env)
    decode_envelope(lean_env)

    rocq_funcs = rocq_env.get("functions", {})
    lean_funcs = lean_env.get("functions", {})
    all_qualnames = sorted(set(rocq_funcs) | set(lean_funcs))

    results: dict[str, QualnameResult] = {}
    for qn in all_qualnames:
        rocq_entry = rocq_funcs.get(qn)
        lean_entry = lean_funcs.get(qn)
        results[qn] = _reconcile_one(qn, rocq_entry, lean_entry)
    return Reconciliation(
        results=results,
        rocq_source=str(rocq_env.get("source", "")),
        lean_source=str(lean_env.get("source", "")),
    )


def _reconcile_one(
    qualname: str,
    rocq_entry: dict[str, Any] | None,
    lean_entry: dict[str, Any] | None,
) -> QualnameResult:
    rocq = decode_contract_clauses(rocq_entry) if rocq_entry else None
    lean = decode_contract_clauses(lean_entry) if lean_entry else None

    if rocq and not lean:
        return QualnameResult(qualname=qualname, status=Status.ROCQ_ONLY,
                              rocq=rocq, lean=None, chosen=rocq)
    if lean and not rocq:
        return QualnameResult(qualname=qualname, status=Status.LEAN_ONLY,
                              rocq=None, lean=lean, chosen=lean)
    assert rocq is not None and lean is not None  # union excludes None+None

    # Compare ensures multisets after canonicalization. We treat
    # requires the same way — they're informationally relevant but
    # functionally less critical for divergence reporting.
    rocq_ensures_canon = _canon_multiset(rocq["ensures"])
    lean_ensures_canon = _canon_multiset(lean["ensures"])
    rocq_requires_canon = _canon_multiset(rocq["requires"])
    lean_requires_canon = _canon_multiset(lean["requires"])

    ensures_diff = _multiset_diff(rocq_ensures_canon, lean_ensures_canon)
    requires_diff = _multiset_diff(rocq_requires_canon, lean_requires_canon)
    variants_agree = _canon_optional(rocq["variant"]) == _canon_optional(lean["variant"])

    if ensures_diff == ([], []) and requires_diff == ([], []) and variants_agree:
        return QualnameResult(
            qualname=qualname, status=Status.RECONCILED,
            rocq=rocq, lean=lean, chosen=rocq,
        )

    rocq_only, lean_only = ensures_diff
    return QualnameResult(
        qualname=qualname, status=Status.DISAGREEMENT,
        rocq=rocq, lean=lean,
        # Default to the rocq side when emission proceeds despite a
        # disagreement (`--on-disagreement=force`). The reverse choice
        # would be equally defensible; the CLI flag pins it.
        chosen=rocq,
        rocq_only_clauses=rocq_only,
        lean_only_clauses=lean_only,
    )


def _canon_multiset(clauses: list[Node]) -> Counter:
    """Map a clause list to a Counter keyed by canonical IR."""
    return Counter(canonicalize(c) for c in clauses)


def _canon_optional(node: Node | None) -> Node | None:
    return canonicalize(node) if node is not None else None


def _multiset_diff(
    a: Counter, b: Counter
) -> tuple[list[Node], list[Node]]:
    """Return `(only_in_a, only_in_b)` as flat lists of Nodes."""
    a_only_counter = a - b
    b_only_counter = b - a
    a_only = [k for k, n in a_only_counter.items() for _ in range(n)]
    b_only = [k for k, n in b_only_counter.items() for _ in range(n)]
    return a_only, b_only
