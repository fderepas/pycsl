r"""Test 2132 — route #236 (expected FAIL since route #334; was a PASS control):  An int default and an
INTEGRAL float default on an int field stay captured: `k: int = 5`, `m: int = 2.0` omitted give
`p.k + p.m == 7`, which PROVED (CPython `5 + 2.0 == 7.0 == 7`, a TRUE claim). Route #334 carries an INTEGRAL float field
as an int only as a DIRECT comparison operand: int arithmetic on it is not float-faithful in general (`r * 10**17 + 1`, corpus 4430),
so `p.k + p.m` is now REFUSED (PYCSL-R325-OPAQUE-INT-FALLBACK) — an over-refusal of a true claim, declared. The comparison form
is control 4444.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class P:
    x: int
    k: int = 5
    m: int = 2.0


#@ ensures \result == 7
#@ assigns \nothing
def g(c: int) -> int:
    p = P(c)
    return p.k + p.m
