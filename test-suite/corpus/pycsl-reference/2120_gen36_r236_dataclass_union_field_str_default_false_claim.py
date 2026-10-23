r"""Test 2120 — route #236 (expected FAIL): `k: Union[int, str] = "w"` omitted
(int carrier) took the definite `0` and `p.k == 0` PROVED; CPython returns 2.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Union


@dataclass
class P:
    x: int
    k: Union[int, str] = "w"


#@ ensures \result == 1
#@ assigns \nothing
def g(c: int) -> int:
    p = P(c)
    if p.k == 0:
        return 1
    return 2
