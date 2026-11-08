r"""Test 2093 — gen #36 (expected PASS): the seam over a record LOCAL that is mutated before
its early return, plus an `if/else` whose two arms both return. The field store
(`p.x = 7`) must reach the returned value. Twin: 2094 (must FAIL).
"""
# pycsl-expected: PASS
from dataclasses import dataclass


@dataclass
class P:
    x: int
    y: int



#@ ensures c > 0 ==> \result.x == 7
#@ ensures c == 0 ==> \result.x == 5
#@ ensures c < 0 ==> \result.x == 1
#@ assigns \nothing
def g(c: int) -> P:
    p = P(1, 2)
    if c > 0:
        p.x = 7
        return p
    if c == 0:
        return P(5, 0)
    else:
        return p
