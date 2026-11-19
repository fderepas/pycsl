r"""Test 4060 -- gen #37 route #315 (expected PASS): CONTROL (expected PASS): a `@dataclass` and a `NamedTuple` (synthesized constructors) are unaffected.
"""
# pycsl-expected: PASS
from typing import List, Dict
from dataclasses import dataclass, field, InitVar
from typing import NamedTuple

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

@dataclass
class P:
    x: int
    y: int = 4

class Q(NamedTuple):
    a: int
    b: int

#@ ensures \result == 10
def f() -> int:
    p = P(3)
    q = Q(1, 2)
    return p.x + p.y + q.a + q.b

if __name__ == "__main__":
    assert f() == 10, f()
