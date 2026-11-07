r"""Test 3302 -- route #283 (expected FAIL): red-team p003: `ident` returns its argument, so `b` IS `a`; the append was invisible to `a` and `len(a) == 1` PROVED; CPython: 2.
Now refused (PYCSL-WHYML-APPEND-UNTRACKED-LIST).
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
    b = ident(a)
    b.append(1)
    return len(a)


if __name__ == "__main__":
    assert f() == 2
