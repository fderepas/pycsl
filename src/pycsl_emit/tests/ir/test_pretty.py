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


# ──────────────────────────────────────────────────────────────────────
# New IR nodes added for the 9-data-type corpus (Phase 1 of tuesday-01).
# ──────────────────────────────────────────────────────────────────────


def test_list_and_array_ops():
    from pycsl_emit.ir import Length, Nth

    expr = Length(arr=Var("arr"))
    assert pretty(expr) == "Length\n  Var(arr)"

    expr2 = Nth(arr=Var("arr"), i=Var("i"))
    assert pretty(expr2) == "Nth\n  Var(arr)\n  Var(i)"


def test_tuple_and_proj():
    from pycsl_emit.ir import Proj, Tuple

    expr = Tuple(args=(Var("a"), Var("b")))
    assert pretty(expr) == "Tuple\n  Var(a)\n  Var(b)"

    expr2 = Proj(t=Var("t"), i=1)
    assert pretty(expr2) == "Proj(1)\n  Var(t)"


def test_map_ops():
    from pycsl_emit.ir import HasKey, MapEmpty, MapGet, MapSet

    expr = MapGet(d=Var("d"), k=Var("k"))
    assert pretty(expr) == "MapGet\n  Var(d)\n  Var(k)"

    expr2 = MapSet(d=Var("d"), k=Var("k"), v=Lit(42))
    assert "MapSet" in pretty(expr2)
    assert "Lit(42)" in pretty(expr2)

    assert pretty(MapEmpty()) == "MapEmpty"
    assert pretty(HasKey(d=Var("d"), k=Var("k"))) == "HasKey\n  Var(d)\n  Var(k)"


def test_string_ops():
    from pycsl_emit.ir import StrConcat, StrLength, StrLit, StrSub

    assert pretty(StrLit("hi")) == "StrLit('hi')"
    assert pretty(StrConcat(a=Var("s"), b=Var("t"))) == "StrConcat\n  Var(s)\n  Var(t)"
    assert pretty(StrLength(s=Var("s"))) == "StrLength\n  Var(s)"
    expr = StrSub(s=Var("s"), lo=Lit(0), hi=Lit(3))
    assert "StrSub" in pretty(expr)


def test_field_get():
    from pycsl_emit.ir import FieldGet

    expr = FieldGet(obj=Var("self"), name="_balance")
    assert pretty(expr) == "FieldGet(_balance)\n  Var(self)"


def test_ghost_list_ops():
    from pycsl_emit.ir import ListAppend, ListCons, ListLen, ListNil, ListNthAt

    assert pretty(ListNil()) == "ListNil"
    assert (
        pretty(ListCons(head=Var("x"), tail=ListNil()))
        == "ListCons\n  Var(x)\n  ListNil"
    )
    assert pretty(ListLen(l=Var("l"))) == "ListLen\n  Var(l)"
    expr = ListAppend(l1=Var("a"), l2=Var("b"))
    assert pretty(expr) == "ListAppend\n  Var(a)\n  Var(b)"
    assert (
        pretty(ListNthAt(l=Var("l"), i=Lit(0))) == "ListNthAt\n  Var(l)\n  Lit(0)"
    )


def test_ghost_set_ops():
    from pycsl_emit.ir import (
        SetAdd,
        SetDiff,
        SetEmpty,
        SetEq,
        SetInter,
        SetMem,
        SetRemove,
        SetSubset,
        SetUnion,
    )

    assert pretty(SetEmpty()) == "SetEmpty"
    assert pretty(SetAdd(s=Var("s"), x=Var("x"))) == "SetAdd\n  Var(s)\n  Var(x)"
    assert (
        pretty(SetRemove(s=Var("s"), x=Var("x"))) == "SetRemove\n  Var(s)\n  Var(x)"
    )
    assert pretty(SetMem(x=Var("x"), s=Var("s"))) == "SetMem\n  Var(x)\n  Var(s)"
    assert (
        pretty(SetUnion(a=Var("a"), b=Var("b"))) == "SetUnion\n  Var(a)\n  Var(b)"
    )
    assert (
        pretty(SetInter(a=Var("a"), b=Var("b"))) == "SetInter\n  Var(a)\n  Var(b)"
    )
    assert pretty(SetDiff(a=Var("a"), b=Var("b"))) == "SetDiff\n  Var(a)\n  Var(b)"
    assert (
        pretty(SetSubset(a=Var("a"), b=Var("b")))
        == "SetSubset\n  Var(a)\n  Var(b)"
    )
    assert pretty(SetEq(a=Var("a"), b=Var("b"))) == "SetEq\n  Var(a)\n  Var(b)"
