"""Translator tests: Lean AST → pycsl_emit IR."""

from __future__ import annotations

import pytest

from pycsl_emit.ir import (
    BinOp,
    Divides,
    Forall,
    Lit,
    Result,
    UnaryOp,
    Var,
)

from lean2pycsl.extractor.lean_ast import (
    Binder,
    BinderShape,
    LApp,
    LBinOp,
    LDvd,
    LForall,
    LLit,
    LTheorem,
    LUnaryOp,
    LUnsupported,
    LVar,
    LeanDef,
)
from lean2pycsl.translator import translate_function
from lean2pycsl.translator.lean import TranslationError


def _bind(name: str, ty: str = "Nat", shape: BinderShape = BinderShape.EXPLICIT) -> Binder:
    return Binder(name=name, ty=ty, shape=shape)


def _gcd_def(measure=None, is_partial: bool = False) -> LeanDef:
    return LeanDef(
        name="gcd",
        params=(_bind("a"), _bind("b")),
        return_ty="Nat",
        is_partial=is_partial,
        measure=measure,
    )


# ──────────────────────────────────────────────────────────────────────
# Binder absorption + \result substitution
# ──────────────────────────────────────────────────────────────────────


def test_gcd_dvd_left_absorbs_outer_binders():
    # theorem gcd_dvd_left : ∀ a b, gcd a b ∣ a
    thm = LTheorem(
        name="gcd_dvd_left",
        binders=(_bind("a"), _bind("b")),
        statement=LDvd(a=LApp("gcd", (LVar("a"), LVar("b"))), b=LVar("a")),
    )
    c = translate_function(_gcd_def(), [thm])
    assert c.ensures == [Divides(d=Result(), n=Var("a"))]
    assert c.requires == [
        BinOp(">=", Var("a"), Lit(0)),
        BinOp(">=", Var("b"), Lit(0)),
    ]
    assert c.assigns == "\\nothing"
    assert c.unsupported == []


def test_top_level_conjunction_splits_into_two_ensures():
    thm = LTheorem(
        name="gcd_dvd",
        binders=(_bind("a"), _bind("b")),
        statement=LBinOp(
            "/\\",
            LDvd(a=LApp("gcd", (LVar("a"), LVar("b"))), b=LVar("a")),
            LDvd(a=LApp("gcd", (LVar("a"), LVar("b"))), b=LVar("b")),
        ),
    )
    c = translate_function(_gcd_def(), [thm])
    assert c.ensures == [
        Divides(d=Result(), n=Var("a")),
        Divides(d=Result(), n=Var("b")),
    ]


def test_unabsorbed_binder_survives_as_forall_with_nat_guard():
    # theorem gcd_greatest : ∀ a b d, d ∣ a → d ∣ b → d ∣ gcd a b
    thm = LTheorem(
        name="gcd_greatest",
        binders=(_bind("a"), _bind("b"), _bind("d")),
        statement=LBinOp(
            "->",
            LDvd(a=LVar("d"), b=LVar("a")),
            LBinOp(
                "->",
                LDvd(a=LVar("d"), b=LVar("b")),
                LDvd(a=LVar("d"), b=LApp("gcd", (LVar("a"), LVar("b")))),
            ),
        ),
    )
    c = translate_function(_gcd_def(), [thm])
    assert len(c.ensures) == 1
    surv = c.ensures[0]
    assert isinstance(surv, Forall)
    assert surv.var == "d" and surv.ty == "Nat"
    # The Nat-guard wraps the body.
    body = surv.body
    assert isinstance(body, BinOp) and body.op == "==>"
    assert body.lhs == BinOp(">=", Var("d"), Lit(0))


# ──────────────────────────────────────────────────────────────────────
# Implicit / instance-implicit binder stripping
# ──────────────────────────────────────────────────────────────────────


def test_implicit_binders_are_stripped_before_absorption():
    """`{Foo : Type}` and `[Inst]` don't appear in the Python signature
    and must be invisible to the absorption pass."""
    func = LeanDef(
        name="f",
        params=(
            _bind("Foo", ty="Type", shape=BinderShape.IMPLICIT),
            _bind("inst", ty="Decidable Foo", shape=BinderShape.INSTANCE_IMPLICIT),
            _bind("x", ty="Nat"),
        ),
        return_ty="Nat",
    )
    thm = LTheorem(
        name="t",
        binders=(_bind("x", "Nat"),),
        statement=LBinOp("=", LApp("f", (LVar("x"),)), LVar("x")),
    )
    c = translate_function(func, [thm])
    # The binder `x` absorbs against the only explicit param `x`.
    # `f x` becomes `Result()` (the function applied to absorbed params).
    assert c.ensures == [BinOp("==", Result(), Var("x"))]
    # The Nat-precondition only emits for explicit Nat params.
    assert c.requires == [BinOp(">=", Var("x"), Lit(0))]


# ──────────────────────────────────────────────────────────────────────
# Type-class quantification rejection (plan §5.7)
# ──────────────────────────────────────────────────────────────────────


def test_theorem_with_polymorphic_binder_is_rejected():
    """A theorem over `[GCDMonoid α]` etc. can't be translated."""
    func = LeanDef(name="gcd", params=(_bind("a"), _bind("b")), return_ty="Nat")
    thm = LTheorem(
        name="gcd_comm",
        binders=(
            _bind("α", ty="GCDMonoid", shape=BinderShape.EXPLICIT),
            _bind("a", ty="α"),
            _bind("b", ty="α"),
        ),
        statement=LBinOp("=", LApp("gcd", (LVar("a"), LVar("b"))), LApp("gcd", (LVar("b"), LVar("a")))),
    )
    c = translate_function(func, [thm], strict=False)
    assert c.ensures == []
    assert len(c.unsupported) == 1
    name, reason, _ = c.unsupported[0]
    assert name == "gcd_comm"
    assert "type class" in reason

    with pytest.raises(TranslationError):
        translate_function(func, [thm], strict=True)


# ──────────────────────────────────────────────────────────────────────
# Termination / variant / diverges
# ──────────────────────────────────────────────────────────────────────


def test_termination_by_extracts_to_variant():
    c = translate_function(_gcd_def(measure=LVar("b")), [])
    assert c.variant == Var("b")
    assert c.diverges is False


def test_partial_def_emits_diverges_not_variant():
    func = LeanDef(
        name="loop",
        params=(),
        return_ty="Nat",
        is_partial=True,
    )
    c = translate_function(func, [])
    assert c.diverges is True
    assert c.variant is None


def test_partial_takes_precedence_over_measure():
    """If a def is both `partial` AND has a `termination_by`, partial
    wins — Lean would have rejected the combination anyway, but we
    should be defensive."""
    func = LeanDef(
        name="loop",
        params=(),
        return_ty="Nat",
        is_partial=True,
        measure=LVar("x"),
    )
    c = translate_function(func, [])
    assert c.diverges is True
    assert c.variant is None


# ──────────────────────────────────────────────────────────────────────
# Operator mapping
# ──────────────────────────────────────────────────────────────────────


def test_operator_map_basic():
    func = LeanDef(name="f", params=(_bind("x"),), return_ty="Nat")
    thm = LTheorem(
        name="t",
        binders=(_bind("x"),),
        statement=LBinOp(
            "/\\",
            LBinOp("=", LVar("x"), LVar("x")),
            LBinOp(
                "/\\",
                LBinOp("<", LBinOp("+", LVar("x"), LLit(1)), LLit(100)),
                LBinOp("=", LBinOp("%", LVar("x"), LLit(2)), LLit(0)),
            ),
        ),
    )
    c = translate_function(func, [thm])
    assert len(c.ensures) == 3
    assert c.ensures[0] == BinOp("==", Var("x"), Var("x"))
    assert c.ensures[1] == BinOp("<", BinOp("+", Var("x"), Lit(1)), Lit(100))
    assert c.ensures[2] == BinOp("==", BinOp("%", Var("x"), Lit(2)), Lit(0))


def test_negation_maps_to_pycsl_not():
    func = LeanDef(name="f", params=(), return_ty="Nat")
    thm = LTheorem(
        name="t",
        binders=(),
        statement=LUnaryOp("~", LBinOp("=", LVar("a"), LVar("b"))),
    )
    c = translate_function(func, [thm])
    assert c.ensures == [UnaryOp("not", BinOp("==", Var("a"), Var("b")))]


def test_int_typed_params_get_no_nat_guard():
    func = LeanDef(
        name="f",
        params=(_bind("x", ty="Int"),),
        return_ty="Int",
    )
    c = translate_function(func, [])
    assert c.requires == []


def test_dvd_with_function_application_substitutes_result():
    # theorem t : ∀ x, 2 ∣ double x
    func = LeanDef(name="double", params=(_bind("x", ty="Int"),), return_ty="Int")
    thm = LTheorem(
        name="t",
        binders=(_bind("x", ty="Int"),),
        statement=LDvd(a=LLit(2), b=LApp("double", (LVar("x"),))),
    )
    c = translate_function(func, [thm])
    assert c.ensures == [Divides(d=Lit(2), n=Result())]


# ──────────────────────────────────────────────────────────────────────
# Unsupported handling
# ──────────────────────────────────────────────────────────────────────


def test_unsupported_node_yields_warning_under_relaxed_mode():
    func = LeanDef(name="f", params=(), return_ty="Nat")
    thm = LTheorem(
        name="t",
        binders=(),
        statement=LUnsupported(reason="higher-order", raw="(fun P => P)"),
    )
    c = translate_function(func, [thm], strict=False)
    assert c.ensures == []
    assert len(c.unsupported) == 1
    assert c.unsupported[0][0] == "t"
    assert "higher-order" in c.unsupported[0][1]


def test_unsupported_node_raises_strict():
    func = LeanDef(name="f", params=(), return_ty="Nat")
    thm = LTheorem(
        name="t",
        binders=(),
        statement=LUnsupported(reason="…", raw="..."),
    )
    with pytest.raises(TranslationError):
        translate_function(func, [thm], strict=True)
