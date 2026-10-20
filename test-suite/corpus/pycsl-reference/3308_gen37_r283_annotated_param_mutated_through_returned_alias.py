r"""Test 3308 -- route #283 (expected FAIL): census, the ANNOTATED twin of 3303 (seq copy): `f(a)` declares `assigns \nothing` and
`b = ident(a); b.append(1)` mutates its OWN PARAMETER through the returned alias; `len(a) == 1` PROVED;
CPython: 2. Now refused (PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS).
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
    b: List[int] = ident(a)
    b.append(1)
    return len(a)


if __name__ == "__main__":
    assert f([0]) == 2
