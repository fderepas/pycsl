r"""Test 2091 — gen #36 (expected FAIL): NON-VACUITY twin of 2090 — every path returns a
record whose `x` is 3, so `\result.x == 4` must NOT prove (an unproved goal, not a type
error).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class P:
    x: int
    y: int



#@ ensures \result.x == 4
#@ assigns \nothing
def f(c: int) -> P:
    if c > 0:
        return P(3, c)
    return P(3, 0)
