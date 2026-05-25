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
