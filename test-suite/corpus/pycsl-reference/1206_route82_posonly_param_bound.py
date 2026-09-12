"""Test 1206 — ROUTE #82, the POSITIONAL-ONLY carrier.

`ast.arguments.posonlyargs` was not read either, so `def __init__(self, v: int, /)` was ALSO
seen as a constructor with no parameters and `P(7).v` proved `\\result == 0` where CPython
returns 7.

A positional-only parameter DOES bind positionally, so it belongs in `init_params` in Python's
own order (`posonlyargs + args`) rather than in the keyword-only side channel — getting that
split wrong would have bound keyword-only names from positional arguments, which is a different
wrong model rather than a fix.

**THE CENSUS FOUND ZERO POSITIONAL-ONLY CONSTRUCTORS ANYWHERE IN THE REPOSITORY**, so this
carrier costs nothing to cover and is covered for the same reason #77 covered its dynamic-bound
case: a guard that is correct only for the spellings that happen to exist today is a guard
waiting to fail open.

This file proves the TRUE claim (7).
"""


class P:
    v: int

    #@ assigns self.v
    def __init__(self, v: int, /) -> None:
        self.v = v


#@ requires True
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    p = P(7)
    return p.v
