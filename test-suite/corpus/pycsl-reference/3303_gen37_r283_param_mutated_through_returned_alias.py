r"""Test 3303 -- route #283 (expected FAIL): red-team p019: `f(a)` declares `assigns \nothing` and
`b = ident(a); b.append(1)` mutates its OWN PARAMETER through the returned alias; `len(a) == 1` PROVED;
CPython: 2. Now refused (PYCSL-WHYML-APPEND-UNTRACKED-LIST).
"""
# pycsl-expected: FAIL
from typing import List


#@ assigns \nothing
def ident(x: List[int]) -> List[int]:
    return x


#@ requires len(a) == 1
#@ ensures \result == 1
#@ assigns \nothing
def f(a: List[int]) -> int:
    b = ident(a)
    b.append(1)
    return len(a)


if __name__ == "__main__":
    assert f([0]) == 2
