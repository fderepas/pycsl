"""IR → PyCSL surface-syntax string.

Walks an IR `Node` and produces a PyCSL contract expression. Atoms
(`Var`, `Lit`, `Result`, `App`) are emitted bare; composite nodes wrap
themselves in parentheses when they appear *inside* another composite,
following the "explicit parenthesization (no precedence hacks)" rule in
rocq2pycsl-plan.md §3 step 2.

PyCSL note: boolean literals are not accepted in contract expressions.
We encode `Lit(True)` as `1 == 1` and `Lit(False)` as `0 == 1` per the
pycsl-annotate skill convention.

The renderer is *pure*. It takes a `NameMap` for identifier remapping
and a `DividesStyle` for the `Divides` encoding decision. Everything else
about the surface form is fixed by the IR.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from ..ir.nodes import (
    App,
    BinOp,
    Divides,
    Exists,
    Forall,
    Lit,
    Node,
    Result,
    UnaryOp,
    Unsupported,
    Var,
)
from .divides import DividesStyle, render_divides
from .names import NameMap
from .opmap import assert_binop, assert_unaryop


_RESULT_LITERAL = "\\result"
_TRUE_LITERAL = "1 == 1"     # PyCSL convention: bare True/False are forbidden
_FALSE_LITERAL = "0 == 1"


@dataclass
class _State:
    """Renderer state. Carries the existential counter so each `Divides`
    in EXISTENTIAL style picks a unique bound variable."""
    names: NameMap
    style: DividesStyle
    _k_counter: int = 0

    def fresh_k(self) -> str:
        self._k_counter += 1
        return f"_k{self._k_counter}"


def render(
    node: Node,
    *,
    names: NameMap | None = None,
    style: DividesStyle = DividesStyle.OPERATIONAL,
) -> str:
    """Render `node` as a PyCSL surface-syntax string.

    The outermost expression is NOT parenthesized. Anything composite
    appearing inside another composite *is* parenthesized.
    """
    state = _State(names=names or NameMap.identity(), style=style)
    return _render_top(node, state)


def _render_top(node: Node, st: _State) -> str:
    """Render at the outer position — no enclosing parens."""
    return _render(node, st, paren=False)


def _render_inner(node: Node, st: _State) -> str:
    """Render in an inner position — composite nodes get parens."""
    return _render(node, st, paren=True)


def _render(node: Node, st: _State, *, paren: bool) -> str:
    # Atoms: no parens regardless of position.
    if isinstance(node, Var):
        return st.names.apply(node.name)
    if isinstance(node, Result):
        return _RESULT_LITERAL
    if isinstance(node, Lit):
        if isinstance(node.value, bool):
            return _TRUE_LITERAL if node.value else _FALSE_LITERAL
        return str(node.value)
    if isinstance(node, App):
        args = ", ".join(_render_top(a, st) for a in node.args)
        return f"{st.names.apply(node.fn)}({args})"
    if isinstance(node, Unsupported):
        raise ValueError(
            f"cannot render Unsupported IR node "
            f"(reason: {node.reason!r}, raw: {node.raw!r})"
        )

    # Composites.
    if isinstance(node, BinOp):
        assert_binop(node.op)
        out = f"{_render_inner(node.lhs, st)} {node.op} {_render_inner(node.rhs, st)}"
        return f"({out})" if paren else out
    if isinstance(node, UnaryOp):
        assert_unaryop(node.op)
        sep = " " if node.op == "not" else ""
        out = f"{node.op}{sep}{_render_inner(node.arg, st)}"
        return f"({out})" if paren else out
    if isinstance(node, Forall):
        var = st.names.apply(node.var)
        # The body is *not* parenthesized; the `;` already disambiguates.
        out = f"\\forall {var}; {_render_top(node.body, st)}"
        return f"({out})" if paren else out
    if isinstance(node, Exists):
        var = st.names.apply(node.var)
        out = f"\\exists {var}; {_render_top(node.body, st)}"
        return f"({out})" if paren else out
    if isinstance(node, Divides):
        d_str = _render_inner(node.d, st)
        n_str = _render_inner(node.n, st)
        k = st.fresh_k() if st.style is DividesStyle.EXISTENTIAL else "_k"
        out = render_divides(d_str, n_str, st.style, k_var=k)
        # Divides expansions are always composite — parenthesize when nested.
        return f"({out})" if paren else out

    raise TypeError(f"render: unknown IR node {type(node).__name__}")


def render_lines(
    nodes: list[Node],
    *,
    names: NameMap | None = None,
    style: DividesStyle = DividesStyle.OPERATIONAL,
) -> list[str]:
    """Convenience: render a list of nodes (one PyCSL clause per node).

    Useful when a single theorem's top-level conjunction has been split
    into separate `ensures` clauses upstream (per rocq2pycsl-plan §5.3).
    """
    return [render(n, names=names, style=style) for n in nodes]
