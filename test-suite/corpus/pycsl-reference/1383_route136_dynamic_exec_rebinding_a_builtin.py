r"""Test 1383 — ROUTE #136: the dynamic twin of test 1366. `exec("le" + "n = sum")` is not a constant `exec`, so neither the splice nor the #132 exec-token rule sees it; `len(xs)` PROVED `\result == 1` for `xs = [5]` while CPython returns 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List

exec("le" + "n = sum")


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [5]
    return len(xs)
