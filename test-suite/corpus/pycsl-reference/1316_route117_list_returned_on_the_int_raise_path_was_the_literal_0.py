r"""Test 1316 — ROUTE #117 negative: an unannotated function returning a list local early (`if x > 0: return xs`) collapsed that return to the literal 0 on the Return-int path, so `\result == 0` PROVED (CPython [x, 1]). It is now `(any int)`.
"""
# pycsl-expected: FAIL
from typing import Any, List

#@ ensures \result == 0
#@ assigns \nothing
def f(x: int):
    xs: List[int] = [x, 1]
    if x > 0:
        return xs
    return 0
