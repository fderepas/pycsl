r"""Test 3080 — route #279 (expected FAIL): `b = a; b += [1]` — `+=` on a list is an IN-PLACE extend, but the
alias was lowered to a copy (`b := !b ++ ...`), so `len(a) == 1` PROVED at 72ab1c57 (red-team p117).
CPython: 2. Now refused (PYCSL-M6-MUTATION-THROUGH-COLLECTION-ALIAS).
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: List[int] = [0]
    b: List[int] = a
    b += [1]
    return len(a)


if __name__ == "__main__":
    assert f() == 2
