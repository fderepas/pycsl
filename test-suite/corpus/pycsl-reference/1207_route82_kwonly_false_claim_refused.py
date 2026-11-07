"""Test 1207 — ROUTE #82, THE NEGATIVE WITNESS: the false claim must no longer prove.

This is 1204's exploit verbatim — `P(v=7)` then `p.v` claiming `\\result == 0`. Before the
repair it PROVED while CPython returns 7. It must now FAIL, and it must fail because the field
is bound to 7, not because anything is refused: the repair is a faithful capture, so the program
still lowers and proves its TRUE postcondition (1204) while this FALSE one is simply unprovable.

A route is only closed when BOTH directions are locked: 1204 pins the true claim as PROVABLE and
this file pins the false claim as UNPROVABLE. Either one alone would pass for a repair that
merely refused the construct outright, which would have been a completeness regression on 8
constructors — including `PyCSLError` in the self-annotation mirror.

This file is `pycsl-expected: FAIL`.
"""
# pycsl-expected: FAIL


class P:
    v: int

    #@ assigns self.v
    def __init__(self, *, v: int = 0) -> None:
        self.v = v


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    p = P(v=7)
    return p.v
