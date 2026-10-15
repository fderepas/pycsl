r"""Test 2115 — route #236 (expected FAIL): `k: int = None` (an annotation the
default does not satisfy, which CPython runs) omitted: `p.k == 0` PROVED; CPython `None`.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class P:
    x: int
    k: int = None


#@ ensures \result == 1
#@ assigns \nothing
def g(c: int) -> int:
    p = P(c)
    if p.k == 0:
        return 1
    return 2
