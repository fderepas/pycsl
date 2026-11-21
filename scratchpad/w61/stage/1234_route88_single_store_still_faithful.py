"""Test 1234 — ROUTE #88's OVER-BREADTH BOUND: a field with ONE store is untouched.

The #88 repair pops a field's captured default when a LATER top-level store cannot be expressed
by the capture rule. A repair that popped the default for EVERY field — or that keyed on "the
field is stored" rather than "the field is stored AGAIN" — would refuse this file, and would
still satisfy 1228, 1230, 1232 and 1233. This is the negative test for the narrowing itself,
not for the defect: **NEGATIVE-TEST THE NARROWING, NOT JUST THE REPAIR** (the rule route #87's
1225 earned).

It is also the census made executable. The census that priced this repair found ZERO fields
with two top-level stores across 1167 pycsl-reference files, 2217 python-reference files, the
74-file mirror, `src/pycsl` and `src/pycsl_lib` — i.e. every real constructor in this project
is the shape THIS file tests, and none is the shape 1228 tests.
"""


class C:
    n: int
    m: int

    #@ assigns self.n, self.m
    def __init__(self, k: int) -> None:
        self.n = 2
        self.m = k + 1


#@ requires True
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    c = C(7)
    return c.n


#@ requires True
#@ ensures \result == 8
#@ assigns \nothing
def g() -> int:
    c = C(7)
    return c.m
