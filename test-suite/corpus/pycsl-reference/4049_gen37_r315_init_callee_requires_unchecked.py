r"""Test 4049 -- gen #37 route #315 (expected FAIL): `self.n = first(a)` (`requires len(a) >= 1`) under `K([])`: the precondition was never checked and `\result == 1` PROVED (CPython IndexError -> 0). REFUSED.
"""
# pycsl-expected: FAIL
from typing import List

#@ requires len(a) >= 1
#@ ensures \result == a[0]
def first(a: List[int]) -> int:
    return a[0]

class K:
    def __init__(self, a: List[int]) -> None:
        self.n = first(a)

#@ ensures \result == 1
def f() -> int:
    try:
        k = K([])
    except IndexError:
        return 0
    return 1

if __name__ == "__main__":
    assert f() == 1, f()
