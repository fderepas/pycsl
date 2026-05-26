"""Translator tests."""

from __future__ import annotations

import pytest

from pycsl_emit.ir import (
    App,
    BinOp,
    Divides,
    Exists,
    Forall,
    Lit,
    Result,
    UnaryOp,
    Unsupported,
    Var,
)
from pycsl_emit.translator import (
    DividesStyle,
    NameMap,
    render,
)
from pycsl_emit.translator.render import render_lines
from pycsl_emit.translator.opmap import assert_binop, assert_unaryop


# ──────────────────────────────────────────────────────────────────────
# Atoms
# ──────────────────────────────────────────────────────────────────────


def test_var_renders_to_name():
    assert render(Var("a")) == "a"


def test_var_with_namemap():
    nm = NameMap(mapping={"a": "x", "b": "y"})
    assert render(Var("a"), names=nm) == "x"
    assert render(Var("b"), names=nm) == "y"
    assert render(Var("c"), names=nm) == "c"  # identity for unmapped


def test_int_literal():
    assert render(Lit(42)) == "42"
    assert render(Lit(0)) == "0"
    assert render(Lit(-7)) == "-7"


def test_bool_literals_use_pycsl_convention():
    # PyCSL contracts forbid bare True/False; renderer encodes them.
    assert render(Lit(True)) == "1 == 1"
    assert render(Lit(False)) == "0 == 1"


def test_result_marker():
    assert render(Result()) == "\\result"


def test_app_with_zero_args_and_two_args():
    assert render(App("foo", ())) == "foo()"
    assert render(App("gcd", (Var("a"), Var("b")))) == "gcd(a, b)"


# ──────────────────────────────────────────────────────────────────────
# Composites and parenthesization
# ──────────────────────────────────────────────────────────────────────


def test_top_level_binop_has_no_outer_parens():
    expr = BinOp("==", Var("a"), Lit(0))
    assert render(expr) == "a == 0"


def test_nested_binop_gets_parenthesized():
    inner = BinOp("+", Var("a"), Var("b"))
    expr = BinOp("==", inner, Lit(0))
    assert render(expr) == "(a + b) == 0"


def test_three_level_nesting():
    # ((a + b) * c) == 0
    expr = BinOp(
        "==",
        BinOp("*", BinOp("+", Var("a"), Var("b")), Var("c")),
        Lit(0),
    )
    assert render(expr) == "((a + b) * c) == 0"


def test_unary_not_at_top_and_nested():
    assert render(UnaryOp("not", Var("p"))) == "not p"
    nested = BinOp("and", UnaryOp("not", Var("p")), Var("q"))
    assert render(nested) == "(not p) and q"


def test_unary_minus_uses_no_space():
    assert render(UnaryOp("-", Var("a"))) == "-a"


def test_implication_and_iff():
    impl = BinOp("==>", Var("p"), Var("q"))
    iff = BinOp("<==>", Var("p"), Var("q"))
    assert render(impl) == "p ==> q"
    assert render(iff) == "p <==> q"


# ──────────────────────────────────────────────────────────────────────
# Quantifiers
# ──────────────────────────────────────────────────────────────────────


def test_forall_top_level_uses_semicolon_separator():
    expr = Forall("k", "int", BinOp("==", BinOp("*", Var("d"), Var("k")), Var("n")))
    assert render(expr) == "\\forall k; (d * k) == n"


def test_exists_top_level():
    expr = Exists("k", "int", BinOp("==", Var("n"), BinOp("*", Var("d"), Var("k"))))
    assert render(expr) == "\\exists k; n == (d * k)"


def test_forall_quantifier_renamed_by_namemap():
    nm = NameMap(mapping={"x": "i"})
    expr = Forall("x", "nat", BinOp(">=", Var("x"), Lit(0)))
    assert render(expr, names=nm) == "\\forall i; i >= 0"


def test_quantifier_nested_under_binop_gets_parens():
    # Same shape as a postcondition that mixes ∀ inside an implication:
    #   p ==> (∀ d; a % d == 0)
    expr = BinOp(
        "==>",
        Var("p"),
        Forall("d", "int", BinOp("==", BinOp("%", Var("a"), Var("d")), Lit(0))),
    )
    assert render(expr) == "p ==> (\\forall d; (a % d) == 0)"


# ──────────────────────────────────────────────────────────────────────
# Divides
# ──────────────────────────────────────────────────────────────────────


def test_divides_operational_default():
    expr = Divides(d=Var("d"), n=Var("n"))
    assert render(expr) == "n % d == 0"


def test_divides_operational_uses_result_marker_when_arg_is_result():
    expr = Divides(d=Result(), n=Var("a"))
    assert render(expr) == "a % \\result == 0"


def test_divides_existential_uses_fresh_bound_var():
    expr = Divides(d=Var("d"), n=Var("n"))
    out = render(expr, style=DividesStyle.EXISTENTIAL)
    assert out == "\\exists _k1; n == d * _k1"


def test_two_divides_existential_get_distinct_vars():
    # ((d | a) and (d | b)) — both must use distinct bound vars.
    expr = BinOp(
        "and",
        Divides(d=Var("d"), n=Var("a")),
        Divides(d=Var("d"), n=Var("b")),
    )
    out = render(expr, style=DividesStyle.EXISTENTIAL)
    # Each Divides is wrapped in parens because it's inside a BinOp.
    assert "_k1" in out and "_k2" in out
    assert "_k1; a == d * _k1" in out
    assert "_k2; b == d * _k2" in out


def test_divides_guarded_form():
    expr = Divides(d=Var("d"), n=Var("n"))
    out = render(expr, style=DividesStyle.GUARDED)
    assert out == "(d == 0 and n == 0) or (d > 0 and n % d == 0)"


# ──────────────────────────────────────────────────────────────────────
# Worked example: gcd_divides_left
# ──────────────────────────────────────────────────────────────────────


def test_gcd_divides_left_postcondition_after_binder_absorption():
    """After absorbing `forall a b`, the conclusion is `gcd a b | a`,
    which becomes `a % \\result == 0` in PyCSL surface form."""
    expr = Divides(d=Result(), n=Var("a"))
    assert render(expr) == "a % \\result == 0"


def test_gcd_greatest_with_unabsorbed_forall_d():
    """∀ d, (a % d == 0 and b % d == 0) ==> \\result % d == 0"""
    expr = Forall(
        "d", "int",
        BinOp(
            "==>",
            BinOp(
                "and",
                BinOp("==", BinOp("%", Var("a"), Var("d")), Lit(0)),
                BinOp("==", BinOp("%", Var("b"), Var("d")), Lit(0)),
            ),
            BinOp("==", BinOp("%", Result(), Var("d")), Lit(0)),
        ),
    )
    # Inner BinOps are always parenthesized (no precedence hacks); this is the
    # rocq2pycsl-plan §3 step 2 contract.
    expected = (
        "\\forall d; "
        "(((a % d) == 0) and ((b % d) == 0)) ==> ((\\result % d) == 0)"
    )
    assert render(expr) == expected


# ──────────────────────────────────────────────────────────────────────
# Misuse and error reporting
# ──────────────────────────────────────────────────────────────────────


def test_unsupported_node_raises():
    with pytest.raises(ValueError, match="Unsupported IR node"):
        render(Unsupported(reason="higher-order", raw="(fun f => P f)"))


def test_unknown_binop_rejected_in_opmap():
    with pytest.raises(ValueError, match="unknown PyCSL binary operator"):
        assert_binop("xor")


def test_unknown_unaryop_rejected_in_opmap():
    with pytest.raises(ValueError, match="unknown PyCSL unary operator"):
        assert_unaryop("~")


def test_render_lines_one_per_node():
    nodes = [
        Divides(d=Result(), n=Var("a")),
        Divides(d=Result(), n=Var("b")),
    ]
    out = render_lines(nodes)
    assert out == ["a % \\result == 0", "b % \\result == 0"]


# ──────────────────────────────────────────────────────────────────────
# New IR-node surface forms (Phase 1 of tuesday-01 corpus growth)
# ──────────────────────────────────────────────────────────────────────


def test_length_and_nth():
    from pycsl_emit.ir import Length, Nth

    assert render(Length(arr=Var("arr"))) == "\\length(arr)"
    assert render(Nth(arr=Var("arr"), i=Var("i"))) == "arr[i]"
    # `arr[i]` is atom-like: no surrounding parens inside a comparison.
    expr = BinOp(">=", Nth(arr=Var("arr"), i=Var("i")), Lit(0))
    assert render(expr) == "arr[i] >= 0"


def test_tuple_and_proj():
    from pycsl_emit.ir import Proj, Tuple

    assert render(Tuple(args=(Var("a"), Var("b")))) == "\\mktuple(a, b)"
    assert render(Proj(t=Result(), i=0)) == "\\result[0]"
    assert render(Proj(t=Result(), i=1)) == "\\result[1]"


def test_map_ops():
    from pycsl_emit.ir import HasKey, MapEmpty, MapGet, MapSet

    assert render(MapGet(d=Var("d"), k=Var("k"))) == "\\map_get(d, k)"
    assert (
        render(MapSet(d=Var("d"), k=Var("k"), v=Lit(42)))
        == "\\map_set(d, k, 42)"
    )
    assert render(MapEmpty()) == "\\empty_map"
    assert render(HasKey(d=Var("d"), k=Var("k"))) == "\\has_key(d, k)"


def test_string_ops():
    from pycsl_emit.ir import StrConcat, StrLength, StrLit, StrSub

    assert render(StrLit("hello")) == '"hello"'
    assert render(StrConcat(a=Var("s"), b=Var("t"))) == "s ^ t"
    # Nested concat parenthesizes inner concat.
    expr = StrConcat(
        a=StrConcat(a=Var("a"), b=Var("b")), b=Var("c")
    )
    assert render(expr) == "(a ^ b) ^ c"
    assert render(StrLength(s=Var("s"))) == "\\str_length(s)"
    assert (
        render(StrSub(s=Var("s"), lo=Lit(0), hi=Lit(3)))
        == "\\str_sub(s, 0, 3)"
    )


def test_field_get_renders_as_dotted():
    from pycsl_emit.ir import FieldGet

    assert (
        render(FieldGet(obj=Var("self"), name="_balance"))
        == "self._balance"
    )
    # Field access is atom-like: no surrounding parens in a comparison.
    expr = BinOp(">=", FieldGet(obj=Var("self"), name="_balance"), Lit(0))
    assert render(expr) == "self._balance >= 0"


def test_ghost_list_ops():
    from pycsl_emit.ir import ListAppend, ListCons, ListLen, ListNil, ListNthAt

    assert render(ListNil()) == "\\nil"
    assert (
        render(ListCons(head=Var("x"), tail=ListNil()))
        == "\\cons(x, \\nil)"
    )
    assert render(ListLen(l=Var("l"))) == "\\list_length(l)"
    assert (
        render(ListAppend(l1=Var("a"), l2=Var("b")))
        == "\\append(a, b)"
    )
    assert (
        render(ListNthAt(l=Var("l"), i=Lit(0)))
        == "\\nth(l, 0)"
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

    assert render(SetEmpty()) == "\\set_empty"
    assert render(SetAdd(s=Var("s"), x=Var("x"))) == "\\set_add(s, x)"
    assert (
        render(SetRemove(s=Var("s"), x=Var("x"))) == "\\set_remove(s, x)"
    )
    assert render(SetMem(x=Var("x"), s=Var("s"))) == "\\set_mem(x, s)"
    assert render(SetUnion(a=Var("a"), b=Var("b"))) == "\\set_union(a, b)"
    assert render(SetInter(a=Var("a"), b=Var("b"))) == "\\set_inter(a, b)"
    assert render(SetDiff(a=Var("a"), b=Var("b"))) == "\\set_diff(a, b)"
    assert (
        render(SetSubset(a=Var("a"), b=Var("b"))) == "\\set_subset(a, b)"
    )
    assert render(SetEq(a=Var("a"), b=Var("b"))) == "\\set_eq(a, b)"
