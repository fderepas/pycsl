"""Test 1205 — ROUTE #82, the OMITTED-keyword carrier: a keyword-only parameter's NONZERO
DEFAULT.

Binding the keyword arguments that are SUPPLIED is not sufficient. A keyword-only parameter
OMITTED at the call site takes its DEFAULT, and the old literal `0` was right only when that
default happened to BE `0`:

    def __init__(self, *, v: int = 5) -> None: self.v = v
    P().v           #@ ensures \\result == 0     <-- PROVED; CPython returns 5

So the repair also captures each keyword-only parameter's CONSTANT default
(`init_kwonly_defaults`), seeded before the explicit keywords so a supplied keyword still
overrides it. A NON-constant default stays omitted and is route #79's class, not this one.

This file proves the TRUE claim (5): the omitted default is now modelled faithfully.
"""


class P:
    v: int

    #@ assigns self.v
    def __init__(self, *, v: int = 5) -> None:
        self.v = v


#@ requires True
#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    p = P()
    return p.v
