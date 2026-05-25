"""Translate `Divides(d, n)` into PyCSL surface syntax.

Three styles are supported, per rocq2pycsl-plan.md §5.2 /
lean2pycsl-plan.md §5.2:

  OPERATIONAL  →  n % d == 0
                  Concise, SMT-friendly. Caller must guarantee d != 0
                  (a separate precondition typically does this).

  EXISTENTIAL  →  \\exists k; n == d * k
                  Closest to the mathematical definition. Why3 + SMT
                  often struggle with the unbounded existential. The
                  bound variable is named uniquely per call.

  GUARDED      →  (d == 0 and n == 0) or (d > 0 and n % d == 0)
                  Operational form with the d == 0 case spelled out.
                  Safe even when the caller can't establish d > 0.

The renderer is wired in `pycsl_emit.translator.render`; this module
just owns the string production once the surface forms of `d` and `n`
are known.
"""

from __future__ import annotations

import enum


class DividesStyle(str, enum.Enum):
    OPERATIONAL = "operational"
    EXISTENTIAL = "existential"
    GUARDED = "guarded"


def render_divides(d_str: str, n_str: str, style: DividesStyle, k_var: str = "_k") -> str:
    """Emit the PyCSL surface form for `Divides(d, n)`.

    `d_str` and `n_str` are already-rendered (and parenthesized as needed)
    operand strings. `k_var` is the fresh existential bound variable used
    only for the EXISTENTIAL style.
    """
    if style is DividesStyle.OPERATIONAL:
        return f"{n_str} % {d_str} == 0"
    if style is DividesStyle.EXISTENTIAL:
        return f"\\exists {k_var}; {n_str} == {d_str} * {k_var}"
    if style is DividesStyle.GUARDED:
        return (
            f"({d_str} == 0 and {n_str} == 0) "
            f"or ({d_str} > 0 and {n_str} % {d_str} == 0)"
        )
    raise ValueError(f"unknown DividesStyle {style!r}")
