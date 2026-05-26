"""IR pretty printer.

Produces a stable indented representation. Used in unit tests and for
debugging extractor output. *Not* the PyCSL surface — for that, see
pycsl_emit.translator.render.
"""

from __future__ import annotations

from typing import Union

from .nodes import (
    Node,
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
    Unsupported,
    Var,
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

_INDENT = "  "


def pretty(item: Union[Node, Theorem, FunctionDef]) -> str:
    """Render `item` to a stable indented string."""
    return "\n".join(_lines(item, 0))


def _lines(item, depth: int) -> list[str]:
    pad = _INDENT * depth

    if isinstance(item, Var):
        return [f"{pad}Var({item.name})"]
    if isinstance(item, Lit):
        return [f"{pad}Lit({item.value!r})"]
    if isinstance(item, Result):
        return [f"{pad}Result"]
    if isinstance(item, Unsupported):
        return [f"{pad}Unsupported(reason={item.reason!r}, raw={item.raw!r})"]
    if isinstance(item, App):
        out = [f"{pad}App({item.fn})"]
        for a in item.args:
            out.extend(_lines(a, depth + 1))
        return out
    if isinstance(item, BinOp):
        out = [f"{pad}BinOp({item.op})"]
        out.extend(_lines(item.lhs, depth + 1))
        out.extend(_lines(item.rhs, depth + 1))
        return out
    if isinstance(item, UnaryOp):
        out = [f"{pad}UnaryOp({item.op})"]
        out.extend(_lines(item.arg, depth + 1))
        return out
    if isinstance(item, Forall):
        out = [f"{pad}Forall({item.var}: {item.ty})"]
        out.extend(_lines(item.body, depth + 1))
        return out
    if isinstance(item, Exists):
        out = [f"{pad}Exists({item.var}: {item.ty})"]
        out.extend(_lines(item.body, depth + 1))
        return out
    if isinstance(item, Divides):
        out = [f"{pad}Divides"]
        out.extend(_lines(item.d, depth + 1))
        out.extend(_lines(item.n, depth + 1))
        return out

    # Lists / arrays / tuples / dicts / strings
    if isinstance(item, Length):
        out = [f"{pad}Length"]
        out.extend(_lines(item.arr, depth + 1))
        return out
    if isinstance(item, Nth):
        out = [f"{pad}Nth"]
        out.extend(_lines(item.arr, depth + 1))
        out.extend(_lines(item.i, depth + 1))
        return out
    if isinstance(item, Tuple):
        out = [f"{pad}Tuple"]
        for a in item.args:
            out.extend(_lines(a, depth + 1))
        return out
    if isinstance(item, Proj):
        out = [f"{pad}Proj({item.i})"]
        out.extend(_lines(item.t, depth + 1))
        return out
    if isinstance(item, MapGet):
        out = [f"{pad}MapGet"]
        out.extend(_lines(item.d, depth + 1))
        out.extend(_lines(item.k, depth + 1))
        return out
    if isinstance(item, MapSet):
        out = [f"{pad}MapSet"]
        out.extend(_lines(item.d, depth + 1))
        out.extend(_lines(item.k, depth + 1))
        out.extend(_lines(item.v, depth + 1))
        return out
    if isinstance(item, MapEmpty):
        return [f"{pad}MapEmpty"]
    if isinstance(item, HasKey):
        out = [f"{pad}HasKey"]
        out.extend(_lines(item.d, depth + 1))
        out.extend(_lines(item.k, depth + 1))
        return out
    if isinstance(item, StrConcat):
        out = [f"{pad}StrConcat"]
        out.extend(_lines(item.a, depth + 1))
        out.extend(_lines(item.b, depth + 1))
        return out
    if isinstance(item, StrLength):
        out = [f"{pad}StrLength"]
        out.extend(_lines(item.s, depth + 1))
        return out
    if isinstance(item, StrSub):
        out = [f"{pad}StrSub"]
        out.extend(_lines(item.s, depth + 1))
        out.extend(_lines(item.lo, depth + 1))
        out.extend(_lines(item.hi, depth + 1))
        return out
    if isinstance(item, StrLit):
        return [f"{pad}StrLit({item.value!r})"]

    # Class instances
    if isinstance(item, FieldGet):
        out = [f"{pad}FieldGet({item.name})"]
        out.extend(_lines(item.obj, depth + 1))
        return out

    # ghost_list
    if isinstance(item, ListNil):
        return [f"{pad}ListNil"]
    if isinstance(item, ListCons):
        out = [f"{pad}ListCons"]
        out.extend(_lines(item.head, depth + 1))
        out.extend(_lines(item.tail, depth + 1))
        return out
    if isinstance(item, ListLen):
        out = [f"{pad}ListLen"]
        out.extend(_lines(item.l, depth + 1))
        return out
    if isinstance(item, ListAppend):
        out = [f"{pad}ListAppend"]
        out.extend(_lines(item.l1, depth + 1))
        out.extend(_lines(item.l2, depth + 1))
        return out
    if isinstance(item, ListNthAt):
        out = [f"{pad}ListNthAt"]
        out.extend(_lines(item.l, depth + 1))
        out.extend(_lines(item.i, depth + 1))
        return out

    # ghost_set
    if isinstance(item, SetEmpty):
        return [f"{pad}SetEmpty"]
    if isinstance(item, SetAdd):
        out = [f"{pad}SetAdd"]
        out.extend(_lines(item.s, depth + 1))
        out.extend(_lines(item.x, depth + 1))
        return out
    if isinstance(item, SetRemove):
        out = [f"{pad}SetRemove"]
        out.extend(_lines(item.s, depth + 1))
        out.extend(_lines(item.x, depth + 1))
        return out
    if isinstance(item, SetMem):
        out = [f"{pad}SetMem"]
        out.extend(_lines(item.x, depth + 1))
        out.extend(_lines(item.s, depth + 1))
        return out
    if isinstance(item, SetUnion):
        out = [f"{pad}SetUnion"]
        out.extend(_lines(item.a, depth + 1))
        out.extend(_lines(item.b, depth + 1))
        return out
    if isinstance(item, SetInter):
        out = [f"{pad}SetInter"]
        out.extend(_lines(item.a, depth + 1))
        out.extend(_lines(item.b, depth + 1))
        return out
    if isinstance(item, SetDiff):
        out = [f"{pad}SetDiff"]
        out.extend(_lines(item.a, depth + 1))
        out.extend(_lines(item.b, depth + 1))
        return out
    if isinstance(item, SetSubset):
        out = [f"{pad}SetSubset"]
        out.extend(_lines(item.a, depth + 1))
        out.extend(_lines(item.b, depth + 1))
        return out
    if isinstance(item, SetEq):
        out = [f"{pad}SetEq"]
        out.extend(_lines(item.a, depth + 1))
        out.extend(_lines(item.b, depth + 1))
        return out

    if isinstance(item, Theorem):
        binder_str = ", ".join(f"{v}: {t}" for v, t in item.binders)
        out = [f"{pad}Theorem({item.name}, binders=[{binder_str}])"]
        out.extend(_lines(item.statement, depth + 1))
        return out
    if isinstance(item, FunctionDef):
        param_str = ", ".join(f"{v}: {t}" for v, t in item.params)
        out = [f"{pad}FunctionDef({item.name}({param_str}) -> {item.return_ty})"]
        if item.measure is not None:
            out.append(f"{pad}{_INDENT}measure:")
            out.extend(_lines(item.measure, depth + 2))
        return out

    raise TypeError(f"pretty: unknown IR node {type(item).__name__}")
