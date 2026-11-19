r"""Test 4117 -- gen #37 route #319 (expected FAIL): `if b: xs = [7, 7, 7]` was a block-scoped `let`; after the `if` `len(xs)` read the caller list and `\result == 2` PROVED (CPython 3). REFUSED.
"""
# pycsl-expected: FAIL
from typing import List
#@ requires len(xs) == 2
#@ ensures \result == 2
def f(xs: List[int], b: bool) -> int:
    if b:
        xs = [7, 7, 7]
    return len(xs)

if __name__ == "__main__":
    assert f([1, 2], True) == 2, f([1, 2], True)
