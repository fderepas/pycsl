r"""Test 2121 — route #236 (expected FAIL): `k: int = 2.5` omitted:
the class-body collector `int()`-TRUNCATED the default to 2 and `\result == 2` PROVED; CPython
returns 2.5 (route #148's shape on the class-body arm). Now unconstrained.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class P:
    x: int
    k: int = 2.5


#@ ensures \result == 2
#@ assigns \nothing
def g(c: int) -> int:
    p = P(c)
    return p.k
