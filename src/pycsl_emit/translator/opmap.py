"""Operator surface table for PyCSL.

The IR's `BinOp.op` and `UnaryOp.op` strings are already in PyCSL surface
form (see `pycsl_emit.ir.nodes`). This module exists to document the
accepted set and to flag any disallowed op early.
"""

from __future__ import annotations


# PyCSL-accepted binary operators. The CSL grammar (Module2_Parser.py)
# permits all of these in #@ expressions.
BINARY_OPS: frozenset[str] = frozenset({
    # arithmetic
    "+", "-", "*", "/", "//", "%",
    # comparison
    "==", "!=", "<", ">", "<=", ">=",
    # boolean
    "and", "or",
    # implication / iff
    "==>", "<==>",
})


UNARY_OPS: frozenset[str] = frozenset({
    "not",
    "-",
})


def assert_binop(op: str) -> None:
    if op not in BINARY_OPS:
        raise ValueError(
            f"unknown PyCSL binary operator {op!r}; "
            f"valid: {sorted(BINARY_OPS)}"
        )


def assert_unaryop(op: str) -> None:
    if op not in UNARY_OPS:
        raise ValueError(
            f"unknown PyCSL unary operator {op!r}; "
            f"valid: {sorted(UNARY_OPS)}"
        )
