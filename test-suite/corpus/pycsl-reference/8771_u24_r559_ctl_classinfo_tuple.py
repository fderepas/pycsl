r"""Test 8771 -- route #559 (control, expected PASS): builtin type objects only as a classinfo tuple of `isinstance` and as the types of an `except` clause; list elements are values (`len(xs)`, a literal); CPython 3
"""
# pycsl-expected: PASS
from typing import List


#@ ensures \result >= 0
def f(k: int, xs: List[int]) -> int:
    ys = [len(xs), 1]
    c = 0
    if isinstance(k, (int, bool)):
        c = 1
    try:
        c = c + 1
    except (ZeroDivisionError, KeyError):
        c = 0
    return ys[1] + c


if __name__ == "__main__":
    print(f(1, [1, 2]))
