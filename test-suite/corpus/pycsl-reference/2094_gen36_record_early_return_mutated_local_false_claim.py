r"""Test 2094 — gen #36 (expected FAIL): twin of 2093 — the mutated local's store must NOT be
dropped: `c > 0 ==> \result.x == 1` (the pre-store value) must NOT prove.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class P:
    x: int
    y: int



#@ ensures c > 0 ==> \result.x == 1
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
