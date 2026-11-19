r"""Test 4444 -- gen #37 route #334 (expected PASS): control (replaces the arithmetic of 2132): an INTEGRAL float dataclass default on an int field (`m: int = 2.0`) keeps its int model as a direct comparison operand: `p.m == 2 and p.k == 5` PROVES (CPython `2.0 == 2`).
"""
# pycsl-expected: PASS
from dataclasses import dataclass


@dataclass
class P:
    x: int
    k: int = 5
    m: int = 2.0


#@ ensures \result == True
#@ assigns \nothing
def g(c: int) -> bool:
    p = P(c)
    return p.m == 2 and p.k == 5

if __name__ == "__main__":
    assert g(0) == True, g(0)
