"""Selector tests — picking the right theorems per function."""

from __future__ import annotations

import textwrap

import pytest

from rocq2pycsl.extractor.gallina import (
    GApp,
    GBinOp,
    GDivides,
    GFunctionDef,
    GTheorem,
    GVar,
    GallinaModule,
)
from rocq2pycsl.extractor.selector import select


def _module(*theorems: GTheorem) -> GallinaModule:
    return GallinaModule(theorems=theorems, functions=())


def _make_thm(name: str, statement) -> GTheorem:
    return GTheorem(name=name, binders=(("a", "nat"),), statement=statement)


_GCD = GFunctionDef(
    name="gcd",
    params=(("a", "nat"), ("b", "nat")),
    return_ty="nat",
    is_recursive=True,
)


def test_explicit_selection_takes_precedence():
    mod = _module(
        _make_thm("gcd_divides", GDivides(d=GApp("gcd", (GVar("a"), GVar("b"))), n=GVar("a"))),
        _make_thm("gcd_greatest", GVar("a")),  # body doesn't matter for selection
        _make_thm("unrelated", GVar("z")),
    )
    out = select(mod, _GCD, explicit=["gcd_divides", "gcd_greatest"])
    assert out.rule == "explicit"
    assert [t.name for t in out.theorems] == ["gcd_divides", "gcd_greatest"]


def test_explicit_unknown_theorem_raises():
    mod = _module(_make_thm("foo", GVar("a")))
    with pytest.raises(KeyError, match="bar"):
        select(mod, _GCD, explicit=["bar"])


def test_marker_selection_when_no_explicit():
    src = textwrap.dedent("""
        (* @pycsl-spec gcd *)
        Theorem gcd_divides : forall a b : nat, (gcd a b | a).

        Theorem unrelated : 1 = 1.

        (* @pycsl-spec gcd *)
        Theorem gcd_greatest : forall a b d : nat, (d | gcd a b).
    """)
    mod = _module(
        _make_thm("gcd_divides", GVar("a")),
        _make_thm("unrelated", GVar("a")),
        _make_thm("gcd_greatest", GVar("a")),
    )
    out = select(mod, _GCD, raw_source=src)
    assert out.rule == "marker"
    assert [t.name for t in out.theorems] == ["gcd_divides", "gcd_greatest"]


def test_marker_ignores_other_function_tags():
    src = textwrap.dedent("""
        (* @pycsl-spec other_fn *)
        Theorem mine : 1 = 1.
    """)
    mod = _module(_make_thm("mine", GVar("a")))
    out = select(mod, _GCD, raw_source=src)
    assert out.rule == "none"
    assert out.theorems == ()


def test_heuristic_off_by_default():
    """Even when theorems clearly mention the function, default mode
    refuses to pick them — explicit selection is required."""
    mod = _module(
        _make_thm("gcd_divides", GDivides(d=GApp("gcd", (GVar("a"), GVar("b"))), n=GVar("a"))),
    )
    out = select(mod, _GCD)
    assert out.rule == "none"
    assert out.theorems == ()


def test_heuristic_picks_when_enabled():
    mod = _module(
        _make_thm(
            "gcd_divides",
            GDivides(d=GApp("gcd", (GVar("a"), GVar("b"))), n=GVar("a")),
        ),
        _make_thm(
            "unrelated_facts",
            GBinOp("=", GVar("x"), GVar("y")),
        ),
    )
    out = select(mod, _GCD, allow_heuristic=True)
    assert out.rule == "heuristic"
    assert [t.name for t in out.theorems] == ["gcd_divides"]


def test_explicit_overrides_marker_and_heuristic():
    """Even with markers and a heuristic enabled, explicit wins."""
    src = "(* @pycsl-spec gcd *)\nTheorem foo : 1 = 1."
    mod = _module(
        _make_thm("foo", GVar("a")),
        _make_thm("bar", GApp("gcd", (GVar("a"), GVar("b")))),
    )
    out = select(mod, _GCD, explicit=["bar"], raw_source=src, allow_heuristic=True)
    assert out.rule == "explicit"
    assert [t.name for t in out.theorems] == ["bar"]
