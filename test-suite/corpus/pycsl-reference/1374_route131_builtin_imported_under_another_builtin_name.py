r"""Test 1374 — ROUTE #131 (import arm, order 2): `from builtins import sum as len` escaped the first repair draft (keyed on assignment stores); `len(xs)` was lowered as the builtin length and PROVED `\result == 1` for `xs = [5]` while CPython returns 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List
from builtins import sum as len


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [5]
    return len(xs)
