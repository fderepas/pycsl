r"""Test 2132 — route #236 (expected PASS): CONTROL. An int default and an
INTEGRAL float default on an int field stay captured: `k: int = 5`, `m: int = 2.0` omitted give
`p.k + p.m == 7`, which PROVES (CPython `5 + 2.0 == 7.0 == 7`).
"""
# pycsl-expected: PASS
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
