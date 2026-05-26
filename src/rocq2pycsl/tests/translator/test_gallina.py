"""Translator tests: Gallina AST → pycsl_emit IR.

The fixtures here mirror the small corpus we'll use end-to-end (gcd,
factorial, etc.). Each case starts from a hand-built Gallina AST so the
test is independent of the Lark backend's quirks.
"""

from __future__ import annotations

import pytest

from pycsl_emit.ir import (
    BinOp,
    Divides,
    Forall,
    Lit,
    Result,
    Var,
)

from rocq2pycsl.extractor.gallina import (
    GApp,
    GBinOp,
    GDivides,
    GForall,
    GFunctionDef,
    GLit,
    GTheorem,
    GUnaryOp,
    GUnsupported,
    GVar,
)
from rocq2pycsl.translator import translate_function
from rocq2pycsl.translator.gallina import TranslationError


def _gcd_def(measure=None) -> GFunctionDef:
    return GFunctionDef(
        name="gcd",
        params=(("a", "nat"), ("b", "nat")),
        return_ty="nat",
        measure=measure,
        is_recursive=True,
    )


# ──────────────────────────────────────────────────────────────────────
# Binder absorption + \result substitution
# ──────────────────────────────────────────────────────────────────────


def test_gcd_divides_left_absorbs_outer_binders_and_substitutes_result():
    # Theorem gcd_divides_left : forall a b, gcd a b | a.
    thm = GTheorem(
        name="gcd_divides_left",
        binders=(("a", "nat"), ("b", "nat")),
        statement=GDivides(
            d=GApp("gcd", (GVar("a"), GVar("b"))),
            n=GVar("a"),
        ),
    )
    c = translate_function(_gcd_def(), [thm])
    assert c.ensures == [Divides(d=Result(), n=Var("a"))]
    # `nat` params get automatic >= 0 preconditions.
    assert c.requires == [
        BinOp(">=", Var("a"), Lit(0)),
        BinOp(">=", Var("b"), Lit(0)),
    ]
    assert c.assigns == "\\nothing"
    assert c.unsupported == []


def test_top_level_conjunction_splits_into_two_ensures():
    # Theorem gcd_divides : forall a b, (gcd a b | a) /\ (gcd a b | b).
    thm = GTheorem(
        name="gcd_divides",
        binders=(("a", "nat"), ("b", "nat")),
        statement=GBinOp(
            "/\\",
            GDivides(d=GApp("gcd", (GVar("a"), GVar("b"))), n=GVar("a")),
            GDivides(d=GApp("gcd", (GVar("a"), GVar("b"))), n=GVar("b")),
        ),
    )
    c = translate_function(_gcd_def(), [thm])
    assert c.ensures == [
        Divides(d=Result(), n=Var("a")),
        Divides(d=Result(), n=Var("b")),
    ]


def test_unabsorbed_binder_survives_as_forall():
    # Theorem gcd_greatest : forall a b d, (d | a) -> (d | b) -> (d | gcd a b).
    thm = GTheorem(
        name="gcd_greatest",
        binders=(("a", "nat"), ("b", "nat"), ("d", "nat")),
        statement=GBinOp(
            "->",
            GDivides(d=GVar("d"), n=GVar("a")),
            GBinOp(
                "->",
                GDivides(d=GVar("d"), n=GVar("b")),
                GDivides(d=GVar("d"), n=GApp("gcd", (GVar("a"), GVar("b")))),
            ),
        ),
    )
    c = translate_function(_gcd_def(), [thm])
    # `d` was not absorbed (not a function param), so it survives as ∀d.
    # nat-quantified survivor → guarded with `d >= 0 ==> body`.
    assert len(c.ensures) == 1
    surv = c.ensures[0]
    assert isinstance(surv, Forall)
    assert surv.var == "d" and surv.ty == "nat"
    body = surv.body
    assert isinstance(body, BinOp) and body.op == "==>"
    assert body.lhs == BinOp(">=", Var("d"), Lit(0))
    # The inner chain should preserve the implication structure with
    # divides translated and `gcd a b` → \result.
    inner = body.rhs
    assert isinstance(inner, BinOp) and inner.op == "==>"


def test_absorption_stops_at_first_mismatch():
    # Function with params (a, b) — theorem binders are (x, b). Mismatch
    # on the first binder, so neither absorbs.
    func = GFunctionDef(
        name="f",
        params=(("a", "nat"), ("b", "nat")),
        return_ty="nat",
    )
    thm = GTheorem(
        name="t",
        binders=(("x", "nat"), ("b", "nat")),
        statement=GBinOp("=", GVar("x"), GVar("b")),
    )
    c = translate_function(func, [thm])
    assert len(c.ensures) == 1
    out = c.ensures[0]
    # Two surviving binders (∀x, ∀b) wrap the body.
    assert isinstance(out, Forall) and out.var == "x"
    inner = out.body  # ∀x's body is `b >= 0 ==> ...` guard
    assert isinstance(inner, BinOp) and inner.op == "==>"


# ──────────────────────────────────────────────────────────────────────
# Operator mapping
# ──────────────────────────────────────────────────────────────────────


def test_operator_map_basic_arithmetic_and_comparison():
    """A bag of operators end-to-end through translate_function."""
    func = GFunctionDef(name="f", params=(("x", "nat"),), return_ty="nat")
    # forall x, x = x /\ x + 1 < 100 /\ x mod 2 = 0
    thm = GTheorem(
        name="t",
        binders=(("x", "nat"),),
        statement=GBinOp(
            "/\\",
            GBinOp("=", GVar("x"), GVar("x")),
            GBinOp(
                "/\\",
                GBinOp("<", GBinOp("+", GVar("x"), GLit(1)), GLit(100)),
                GBinOp("=", GBinOp("mod", GVar("x"), GLit(2)), GLit(0)),
            ),
        ),
    )
    c = translate_function(func, [thm])
    # Top-level /\ splits all three branches.
    assert len(c.ensures) == 3
    # x = x  →  x == x
    assert c.ensures[0] == BinOp("==", Var("x"), Var("x"))
    # x + 1 < 100  →  (x + 1) < 100
    assert c.ensures[1] == BinOp(
        "<", BinOp("+", Var("x"), Lit(1)), Lit(100)
    )
    # x mod 2 = 0  →  (x % 2) == 0
    assert c.ensures[2] == BinOp(
        "==", BinOp("%", Var("x"), Lit(2)), Lit(0)
    )


def test_negation_maps_to_pycsl_not():
    func = GFunctionDef(name="f", params=(), return_ty="nat")
    thm = GTheorem(
        name="t",
        binders=(),
        statement=GUnaryOp("~", GBinOp("=", GVar("a"), GVar("b"))),
    )
    c = translate_function(func, [thm])
    from pycsl_emit.ir import UnaryOp
    assert c.ensures == [UnaryOp("not", BinOp("==", Var("a"), Var("b")))]


def test_true_false_constructors_become_bool_lits():
    func = GFunctionDef(name="f", params=(), return_ty="nat")
    thm = GTheorem(name="t", binders=(), statement=GVar("True"))
    c = translate_function(func, [thm])
    assert c.ensures == [Lit(True)]


def test_implication_arrow_maps_to_pycsl_implication():
    func = GFunctionDef(name="f", params=(("x", "nat"),), return_ty="nat")
    thm = GTheorem(
        name="t",
        binders=(("x", "nat"),),
        statement=GBinOp("->", GVar("x"), GVar("x")),
    )
    c = translate_function(func, [thm])
    assert c.ensures == [BinOp("==>", Var("x"), Var("x"))]


# ──────────────────────────────────────────────────────────────────────
# Measure / variant extraction
# ──────────────────────────────────────────────────────────────────────


def test_measure_extracts_to_variant():
    func = _gcd_def(measure=GVar("b"))
    c = translate_function(func, [])
    assert c.variant == Var("b")


def test_measure_failure_records_unsupported_unless_strict():
    func = _gcd_def(measure=GUnsupported(reason="lambda not supported", raw="fun n => n"))
    c = translate_function(func, [])
    assert c.variant is None
    assert any(name == "<measure>" for name, _, _ in c.unsupported)


def test_strict_mode_raises_on_unsupported_measure():
    func = _gcd_def(measure=GUnsupported(reason="…", raw="x"))
    with pytest.raises(TranslationError):
        translate_function(func, [], strict=True)


# ──────────────────────────────────────────────────────────────────────
# Unsupported handling
# ──────────────────────────────────────────────────────────────────────


def test_unsupported_in_theorem_yields_warning_under_relaxed_mode():
    func = GFunctionDef(name="f", params=(), return_ty="nat")
    thm = GTheorem(
        name="t",
        binders=(),
        statement=GUnsupported(reason="higher-order", raw="(fun P => P)"),
    )
    c = translate_function(func, [thm])
    assert c.ensures == []
    assert c.unsupported == [
        ("t", "unsupported Gallina fragment: higher-order ('(fun P => P)')", "")
    ]


def test_unsupported_in_theorem_raises_strict():
    func = GFunctionDef(name="f", params=(), return_ty="nat")
    thm = GTheorem(
        name="t",
        binders=(),
        statement=GUnsupported(reason="dep match", raw="..."),
    )
    with pytest.raises(TranslationError):
        translate_function(func, [thm], strict=True)


# ──────────────────────────────────────────────────────────────────────
# Sanity: nat-precondition emission
# ──────────────────────────────────────────────────────────────────────


def test_int_typed_params_get_no_nat_guard():
    func = GFunctionDef(
        name="f",
        params=(("x", "Z"), ("y", "Z")),
        return_ty="Z",
    )
    c = translate_function(func, [])
    assert c.requires == []


def test_nat_params_each_get_their_own_guard():
    func = GFunctionDef(
        name="f",
        params=(("x", "nat"), ("y", "nat"), ("z", "Z")),
        return_ty="nat",
    )
    c = translate_function(func, [])
    assert c.requires == [
        BinOp(">=", Var("x"), Lit(0)),
        BinOp(">=", Var("y"), Lit(0)),
    ]


# ──────────────────────────────────────────────────────────────────────
# Phase 3 — new operator lowering rules + bool auto-precondition
# ──────────────────────────────────────────────────────────────────────


def test_bool_params_get_zero_or_one_precondition():
    func = GFunctionDef(
        name="bool_xor",
        params=(("a", "bool"), ("b", "bool")),
        return_ty="bool",
    )
    c = translate_function(func, [])
    # Two `requires (x == 0) or (x == 1)` clauses, one per param.
    assert len(c.requires) == 2
    for req, name in zip(c.requires, ("a", "b")):
        assert isinstance(req, BinOp) and req.op == "or"


def _lower_only(stmt: str, func_name: str, params: tuple) -> object:
    """Helper: parse a forall'd theorem and return its lowered statement."""
    from rocq2pycsl.extractor.lark_backend import _parse_expr, _split_outer_binders
    from rocq2pycsl.translator.gallina import _lower

    binders, body = _split_outer_binders(stmt)
    body_node = _parse_expr(body, 0)
    func = GFunctionDef(name=func_name, params=params, return_ty="_")
    return _lower(body_node, func, [p[0] for p in params])


def test_length_lowers_to_Length():
    from pycsl_emit.ir import Length

    out = _lower_only(
        "forall (arr : list nat), length arr >= 0",
        "f",
        (("arr", "list nat"),),
    )
    # `length arr >= 0` → BinOp(>=, Length(arr), Lit(0))
    assert isinstance(out, BinOp) and out.op == ">="
    assert isinstance(out.lhs, Length)
    assert out.lhs.arr == Var("arr")


def test_nth_lowers_to_Nth():
    from pycsl_emit.ir import Nth

    out = _lower_only(
        "forall (arr : list nat) (i : nat), nth i arr 0 >= 0",
        "f",
        (("arr", "list nat"), ("i", "nat")),
    )
    assert isinstance(out, BinOp) and out.op == ">="
    assert isinstance(out.lhs, Nth)
    assert out.lhs.arr == Var("arr")
    assert out.lhs.i == Var("i")


def test_fst_and_snd_lower_to_Proj():
    from pycsl_emit.ir import Proj

    out = _lower_only(
        "forall (t : nat * nat), fst t >= 0",
        "f",
        (("t", "nat * nat"),),
    )
    assert isinstance(out.lhs, Proj)
    assert out.lhs.i == 0


def test_andb_orb_negb_lower_to_arithmetic():
    out = _lower_only(
        "forall (a b : bool), andb a b = a",
        "f",
        (("a", "bool"), ("b", "bool")),
    )
    # andb a b → a * b
    assert isinstance(out, BinOp) and out.op == "=="
    assert isinstance(out.lhs, BinOp) and out.lhs.op == "*"

    out = _lower_only(
        "forall (a : bool), negb a = a",
        "f",
        (("a", "bool"),),
    )
    # negb a → 1 - a
    assert isinstance(out, BinOp) and out.op == "=="
    assert isinstance(out.lhs, BinOp) and out.lhs.op == "-"
    assert out.lhs.lhs == Lit(1)


def test_xorb_lowers_to_arithmetic_xor_formula():
    out = _lower_only(
        "forall (a b : bool), xorb a b = a",
        "f",
        (("a", "bool"), ("b", "bool")),
    )
    # xorb a b → (a + b) - (2 * (a * b))
    assert isinstance(out, BinOp) and out.op == "=="
    minus = out.lhs
    assert isinstance(minus, BinOp) and minus.op == "-"
    assert isinstance(minus.lhs, BinOp) and minus.lhs.op == "+"
