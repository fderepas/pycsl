r"""Test 2092 — gen #36 (expected FAIL): BRANCH twin of 2090 — the early return (`c > 0`)
carries `y == c`, so claiming the TAIL branch's `y == 0` on every path must NOT prove.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class P:
    x: int
    y: int



#@ ensures \result.y == 0
#@ assigns \nothing
def f(c: int) -> P:
    if c > 0:
        return P(3, c)
    return P(3, 0)
