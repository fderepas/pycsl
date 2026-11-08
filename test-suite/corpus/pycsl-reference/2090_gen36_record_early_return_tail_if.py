r"""Test 2090 — gen #36 (expected PASS): EARLY RETURN OF A RECORD. A record-returning
function with an `if ...: return <record>` followed by a tail `return <record>`. At base
the early return lowered to `raise (Return <record>)` against `exception Return int` — a
Why3 type error (refused). Every return is in TAIL position of the if-tree, so the seam
lowers the function to an if-then-else EXPRESSION (no exception) and the returned record's
fields are tracked per branch. Twins: 2091 / 2092 (must FAIL on an unproved goal).
"""
# pycsl-expected: PASS
from dataclasses import dataclass


@dataclass
class P:
    x: int
    y: int



#@ ensures \result.x == 3
#@ ensures c > 0 ==> \result.y == c
#@ ensures c <= 0 ==> \result.y == 0
#@ assigns \nothing
def f(c: int) -> P:
    if c > 0:
        return P(3, c)
    return P(3, 0)
