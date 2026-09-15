r"""Test 1365 — ROUTE #131: `len = sum` at module scope; `len(xs)` was still lowered as the builtin length and PROVED `\result == 1` for `xs = [5]` while CPython returns 5. A builtin rebound by an assignment in a scope where it is called is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List

len = sum


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [5]
    return len(xs)
