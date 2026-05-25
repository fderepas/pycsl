"""IR pretty-printer snapshot tests.

Builds the IR for `gcd_divides` and friends by hand and checks the
rendered shape. These fixtures serve double duty: they're the contract
the extractors (lean2pycsl, rocq2pycsl) must reproduce from their
surface inputs.
"""

from __future__ import annotations

import textwrap

from pycsl_emit.ir import (
    App,
    BinOp,
    Divides,
    Exists,
    Forall,
    FunctionDef,
    Lit,
    Result,
    Theorem,
    UnaryOp,
    Var,
    pretty,
)


def test_gcd_divides_left():
    """∀ a b, gcd a b | a — outer foralls absorbed downstream."""
    t = Theorem(
        name="gcd_divides_left",
        binders=(("a", "nat"), ("b", "nat")),
        statement=Divides(d=App("gcd", (Var("a"), Var("b"))), n=Var("a")),
    )
    expected = textwrap.dedent(
        """\
        Theorem(gcd_divides_left, binders=[a: nat, b: nat])
          Divides
            App(gcd)
              Var(a)
              Var(b)
            Var(a)"""
    )
    assert pretty(t) == expected


def test_gcd_greatest_with_inner_forall():
    """∀ a b d, d|a ∧ d|b → d|gcd a b — `d` survives binder absorption."""
    t = Theorem(
        name="gcd_greatest",
        binders=(("a", "nat"), ("b", "nat"), ("d", "nat")),
        statement=BinOp(
            op="==>",
            lhs=BinOp(
                op="and",
                lhs=Divides(d=Var("d"), n=Var("a")),
                rhs=Divides(d=Var("d"), n=Var("b")),
            ),
            rhs=Divides(d=Var("d"), n=App("gcd", (Var("a"), Var("b")))),
        ),
    )
    rendered = pretty(t)
    # Smoke checks — exact-string match in the simpler test above is enough;
    # here we assert key structural anchors are present.
    assert "Theorem(gcd_greatest" in rendered
    assert "BinOp(==>)" in rendered
    assert "BinOp(and)" in rendered
    # Three Divides nodes total (two on the LHS, one on the RHS).
    assert rendered.count("Divides") == 3


def test_existential_form_of_divides():
    """The faithful encoding: ∃ k, n = d * k."""
    expr = Exists(
        var="k",
        ty="int",
        body=BinOp(op="==", lhs=Var("n"), rhs=BinOp(op="*", lhs=Var("d"), rhs=Var("k"))),
    )
    expected = textwrap.dedent(
        """\
        Exists(k: int)
          BinOp(==)
            Var(n)
            BinOp(*)
              Var(d)
              Var(k)"""
    )
    assert pretty(expr) == expected


def test_function_def_with_measure():
    f = FunctionDef(
        name="gcd",
        params=(("a", "nat"), ("b", "nat")),
        return_ty="nat",
        measure=Var("b"),
    )
    expected = textwrap.dedent(
        """\
        FunctionDef(gcd(a: nat, b: nat) -> nat)
          measure:
            Var(b)"""
    )
    assert pretty(f) == expected


def test_result_and_unary_neg_and_bool_literal():
    expr = UnaryOp(op="not", arg=BinOp(op="==", lhs=Result(), rhs=Lit(False)))
    expected = textwrap.dedent(
        """\
        UnaryOp(not)
          BinOp(==)
            Result
            Lit(False)"""
    )
    assert pretty(expr) == expected


def test_pretty_is_pure_and_deterministic():
    # Same input → identical output across calls.
    expr = BinOp(op="and", lhs=Var("a"), rhs=Var("b"))
    assert pretty(expr) == pretty(expr)
