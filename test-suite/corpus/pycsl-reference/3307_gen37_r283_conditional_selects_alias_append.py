r"""Test 3307 -- route #283 (expected FAIL): census: `b: List[int] = a if c > 0 else [9]` selects `a` itself; the append on the copy PROVED `len(a) == 1`; CPython: 2.
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
    c = 1
    b: List[int] = a if c > 0 else [9]
    b.append(1)
    return len(a)


if __name__ == "__main__":
    assert f() == 2
