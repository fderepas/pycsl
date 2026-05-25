"""Selector tests for lean2pycsl."""

from __future__ import annotations

import pytest

from lean2pycsl.extractor.lean_ast import (
    Binder,
    BinderShape,
    LeanDef,
    LeanModule,
    LDvd,
    LTheorem,
    LVar,
)
from lean2pycsl.extractor.selector import select


def _module(*theorems: LTheorem) -> LeanModule:
    return LeanModule(theorems=theorems, defs=())


def _thm(name: str, target: str | None = None) -> LTheorem:
    return LTheorem(
        name=name,
        binders=(Binder("a", "Nat", BinderShape.EXPLICIT),),
        statement=LDvd(a=LVar("a"), b=LVar("a")),
        pycsl_spec_target=target,
    )


_GCD = LeanDef(
    name="gcd",
    params=(Binder("a", "Nat", BinderShape.EXPLICIT),),
    return_ty="Nat",
)


def test_attribute_selection_is_primary():
    mod = _module(
        _thm("gcd_dvd_left", target="gcd"),
        _thm("gcd_dvd_right", target="gcd"),
        _thm("unrelated", target=None),
    )
    out = select(mod, _GCD)
    assert out.rule == "attribute"
    assert [t.name for t in out.theorems] == ["gcd_dvd_left", "gcd_dvd_right"]


def test_attribute_target_can_differ_from_func_name():
    """`@[pycsl_spec "compute_gcd"]` on a theorem matches a function
    config that uses `target_qualname="compute_gcd"`."""
    mod = _module(_thm("foo", target="compute_gcd"))
    out = select(mod, _GCD, target_qualname="compute_gcd")
    assert out.theorems[0].name == "foo"


def test_extra_specs_complement_attribute_selection():
    mod = _module(
        _thm("from_attr", target="gcd"),
        _thm("from_toml", target=None),
    )
    out = select(mod, _GCD, extra_specs=["from_toml"])
    assert out.rule == "both"
    assert [t.name for t in out.theorems] == ["from_attr", "from_toml"]


def test_extra_specs_without_any_attribute_match():
    mod = _module(_thm("only_one", target=None))
    out = select(mod, _GCD, extra_specs=["only_one"])
    assert out.rule == "extra_specs"
    assert [t.name for t in out.theorems] == ["only_one"]


def test_extra_specs_unknown_theorem_raises():
    mod = _module(_thm("existing", target=None))
    with pytest.raises(KeyError, match="missing"):
        select(mod, _GCD, extra_specs=["missing"])


def test_no_heuristic_returns_none():
    """Unlike rocq2pycsl, lean2pycsl never falls back to heuristic
    mention-scanning — plan §6, last paragraph."""
    mod = _module(_thm("mentions_gcd", target=None))
    out = select(mod, _GCD)
    assert out.rule == "none"
    assert out.theorems == ()


def test_extra_specs_dedupes_against_attribute():
    """If a theorem is both tagged AND named in extra_specs, only
    one copy appears in the result."""
    mod = _module(_thm("both", target="gcd"))
    out = select(mod, _GCD, extra_specs=["both"])
    assert len(out.theorems) == 1
    assert out.theorems[0].name == "both"
