"""Round-trip tests for the IR JSON encoder/decoder.

The bridge depends on these being lossless — any drift here means the
canonicalizer compares non-equivalent trees.
"""

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
    from_dict,
    from_json,
    to_dict,
    to_json,
    Length,
    Nth,
    Tuple,
    Proj,
    MapGet,
    MapSet,
    MapEmpty,
    HasKey,
    StrConcat,
    StrLength,
    StrSub,
    StrLit,
    FieldGet,
    ListNil,
    ListCons,
    ListLen,
    ListAppend,
    ListNthAt,
    SetEmpty,
    SetAdd,
    SetRemove,
    SetMem,
    SetUnion,
    SetInter,
    SetDiff,
    SetSubset,
    SetEq,
)


_CASES = [
    Var("a"),
    Lit(42),
    Lit(True),
    Lit(False),
    Result(),
    App("gcd", (Var("a"), Var("b"))),
    BinOp("+", Var("a"), Lit(1)),
    UnaryOp("not", Var("p")),
    Forall("d", "int", BinOp("==", BinOp("%", Var("a"), Var("d")), Lit(0))),
    Exists("k", "int", BinOp("==", Var("n"), BinOp("*", Var("d"), Var("k")))),
    Divides(d=Result(), n=Var("a")),
    Unsupported(reason="higher-order", raw="(fun P => P)"),
    # New nodes — list/array/tuple/dict/string
    Length(arr=Var("arr")),
    Nth(arr=Var("arr"), i=Var("i")),
    Tuple(args=(Var("a"), Var("b"), Lit(7))),
    Proj(t=Var("t"), i=1),
    MapGet(d=Var("d"), k=Var("k")),
    MapSet(d=Var("d"), k=Var("k"), v=Lit(42)),
    MapEmpty(),
    HasKey(d=Var("d"), k=Var("k")),
    StrConcat(a=Var("s"), b=Var("t")),
    StrLength(s=Var("s")),
    StrSub(s=Var("s"), lo=Lit(0), hi=Lit(3)),
    StrLit("hello"),
    # Class instances
    FieldGet(obj=Var("self"), name="_balance"),
    # ghost_list
    ListNil(),
    ListCons(head=Var("x"), tail=ListNil()),
    ListLen(l=Var("l")),
    ListAppend(l1=Var("a"), l2=Var("b")),
    ListNthAt(l=Var("l"), i=Lit(0)),
    # ghost_set
    SetEmpty(),
    SetAdd(s=Var("s"), x=Var("x")),
    SetRemove(s=Var("s"), x=Var("x")),
    SetMem(x=Var("x"), s=Var("s")),
    SetUnion(a=Var("a"), b=Var("b")),
    SetInter(a=Var("a"), b=Var("b")),
    SetDiff(a=Var("a"), b=Var("b")),
    SetSubset(a=Var("a"), b=Var("b")),
    SetEq(a=Var("a"), b=Var("b")),
]


@pytest.mark.parametrize("node", _CASES, ids=lambda n: type(n).__name__)
def test_dict_round_trip(node):
    assert from_dict(to_dict(node)) == node


@pytest.mark.parametrize("node", _CASES, ids=lambda n: type(n).__name__)
def test_json_round_trip(node):
    assert from_json(to_json(node)) == node


def test_nested_structure_preserves_layout():
    # ∀d; (a % d == 0 and b % d == 0) ==> \result % d == 0
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
    assert from_json(to_json(expr)) == expr


def test_unknown_node_type_rejected():
    with pytest.raises(ValueError, match="unknown node type"):
        from_dict({"type": "Bogus"})
