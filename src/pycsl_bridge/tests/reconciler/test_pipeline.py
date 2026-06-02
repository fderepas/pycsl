"""Reconciler tests.

Build IR-dump envelope dicts by hand (one per side) and assert the
reconciler classifies each qualname correctly.
"""

from __future__ import annotations

from typing import Any

import pytest

from pycsl_emit.ir import (
    BinOp,
    Divides,
    Exists,
    Lit,
    Result,
    Var,
    to_dict,
)

from pycsl_bridge.reconciler import (
    Status,
    format_disagreement,
    reconcile_envelopes,
)


def _entry(theorems, ensures, *, requires=None, variant=None) -> dict[str, Any]:
    return {
        "python_name": "fn",
        "theorems": list(theorems),
        "divides_style": "operational",
        "contract": {
            "requires": [to_dict(r) for r in (requires or [])],
            "ensures": [to_dict(e) for e in ensures],
            "assigns": "\\nothing",
            "variant": to_dict(variant) if variant is not None else None,
            "diverges": False,
            "unsupported": [],
        },
    }


def _envelope(provenance: str, **functions) -> dict[str, Any]:
    return {
        "schema": "pycsl-ir-dump",
        "version": 1,
        "provenance": provenance,
        "source": f"{provenance}-source",
        "functions": functions,
    }


# ──────────────────────────────────────────────────────────────────────


def test_identical_contracts_reconcile():
    rocq = _envelope(
        "rocq2pycsl",
        double=_entry(
            theorems=["double_is_even"],
            ensures=[Divides(d=Lit(2), n=Result())],
        ),
    )
    lean = _envelope(
        "lean2pycsl",
        double=_entry(
            theorems=["double_is_even"],
            ensures=[Divides(d=Lit(2), n=Result())],
        ),
    )
    rec = reconcile_envelopes(rocq, lean)
    assert list(rec.results.keys()) == ["double"]
    assert rec.results["double"].status is Status.RECONCILED
    assert len(rec.disagreements) == 0


def test_existential_form_reconciles_with_operational_form():
    """The headline cross-prover test: one side emits Divides, the
    other emits the existential ∃ k; n == d*k. After canonicalization
    they're the same — reconciler must agree."""
    rocq = _envelope(
        "rocq2pycsl",
        double=_entry(
            theorems=["double_is_even"],
            ensures=[Divides(d=Lit(2), n=Result())],
        ),
    )
    lean = _envelope(
        "lean2pycsl",
        double=_entry(
            theorems=["double_is_even"],
            ensures=[Exists(
                "k", "int",
                BinOp("==", Result(), BinOp("*", Lit(2), Var("k"))),
            )],
        ),
    )
    rec = reconcile_envelopes(rocq, lean)
    assert rec.results["double"].status is Status.RECONCILED


def test_clause_order_does_not_matter():
    """Reconcile via multiset equality: clause order is irrelevant."""
    a = Divides(d=Result(), n=Var("a"))
    b = Divides(d=Result(), n=Var("b"))
    rocq = _envelope("rocq2pycsl", gcd=_entry(theorems=["gcd_divides"], ensures=[a, b]))
    lean = _envelope("lean2pycsl", gcd=_entry(theorems=["gcd_dvd_left", "gcd_dvd_right"], ensures=[b, a]))
    rec = reconcile_envelopes(rocq, lean)
    assert rec.results["gcd"].status is Status.RECONCILED


def test_extra_clause_on_one_side_is_a_disagreement():
    rocq = _envelope(
        "rocq2pycsl",
        f=_entry(theorems=["t1"], ensures=[Var("p")]),
    )
    lean = _envelope(
        "lean2pycsl",
        f=_entry(theorems=["t1", "t2"], ensures=[Var("p"), Var("q")]),
    )
    rec = reconcile_envelopes(rocq, lean)
    r = rec.results["f"]
    assert r.status is Status.DISAGREEMENT
    # Lean has an extra clause (`q`) — it appears in lean_only.
    assert r.lean_only_clauses == [Var("q")]
    assert r.rocq_only_clauses == []


def test_rocq_only_when_lean_envelope_omits_function():
    rocq = _envelope("rocq2pycsl", f=_entry(theorems=["t"], ensures=[Var("p")]))
    lean = _envelope("lean2pycsl")
    rec = reconcile_envelopes(rocq, lean)
    assert rec.results["f"].status is Status.ROCQ_ONLY


def test_lean_only_when_rocq_envelope_omits_function():
    rocq = _envelope("rocq2pycsl")
    lean = _envelope("lean2pycsl", f=_entry(theorems=["t"], ensures=[Var("p")]))
    rec = reconcile_envelopes(rocq, lean)
    assert rec.results["f"].status is Status.LEAN_ONLY


def test_variant_mismatch_is_disagreement():
    rocq = _envelope(
        "rocq2pycsl",
        gcd=_entry(theorems=["t"], ensures=[Var("p")], variant=Var("a")),
    )
    lean = _envelope(
        "lean2pycsl",
        gcd=_entry(theorems=["t"], ensures=[Var("p")], variant=Var("b")),
    )
    rec = reconcile_envelopes(rocq, lean)
    assert rec.results["gcd"].status is Status.DISAGREEMENT


def test_invalid_envelope_schema_raises():
    bogus = {"schema": "not-pycsl", "version": 1, "functions": {}}
    with pytest.raises(ValueError, match="not a pycsl-ir-dump"):
        reconcile_envelopes(bogus, _envelope("lean2pycsl"))


# ──────────────────────────────────────────────────────────────────────
# Diff formatter
# ──────────────────────────────────────────────────────────────────────


def test_format_disagreement_includes_theorem_names_and_clauses():
    rocq = _envelope(
        "rocq2pycsl",
        f=_entry(theorems=["t1"], ensures=[Var("p")]),
    )
    lean = _envelope(
        "lean2pycsl",
        f=_entry(theorems=["t2"], ensures=[Var("p"), Var("q")]),
    )
    rec = reconcile_envelopes(rocq, lean)
    out = format_disagreement(rec.results["f"])
    assert "DISAGREEMENT" in out
    assert "f" in out
    assert "t1" in out
    assert "t2" in out
    assert "+lean" in out
    # No clauses appear on the rocq side, so no "+rocq" line.
    assert "+rocq" not in out


def test_format_reconciled_is_short():
    rocq = _envelope("rocq2pycsl", f=_entry(theorems=["t"], ensures=[Var("p")]))
    lean = _envelope("lean2pycsl", f=_entry(theorems=["t"], ensures=[Var("p")]))
    rec = reconcile_envelopes(rocq, lean)
    out = format_disagreement(rec.results["f"])
    assert "RECONCILED" in out
    assert "\n" not in out


def test_format_one_sided_includes_helpful_hint():
    rocq = _envelope("rocq2pycsl", f=_entry(theorems=["t"], ensures=[Var("p")]))
    lean = _envelope("lean2pycsl")
    rec = reconcile_envelopes(rocq, lean)
    out = format_disagreement(rec.results["f"])
    assert "ROCQ-ONLY" in out
    assert "Lean" in out  # nudges the user to add the Lean side
