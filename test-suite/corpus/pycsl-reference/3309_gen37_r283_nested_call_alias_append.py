r"""Test 3309 -- route #283 (expected FAIL): census: `b: List[int] = ident(ident(a))` -- the alias through two returns -- PROVED `len(a) == 1`; CPython: 2.
Now refused (PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS).
"""
# pycsl-expected: FAIL
from typing import List


#@ assigns \nothing
def ident(x: List[int]) -> List[int]:
    return x


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: List[int] = [0]
    b: List[int] = ident(ident(a))
    b.append(1)
    return len(a)


if __name__ == "__main__":
    assert f() == 2
