r"""Test 1366 — ROUTE #131 (exec arm): `exec("len = sum")` is spliced in as source AFTER the front-end rebinding checks, so `len(xs)` PROVED `\result == 1` for `xs = [5]` while CPython returns 5. A constant `exec` naming a builtin, an imported name or a folded constant is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List

exec("len = sum")


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [5]
    return len(xs)
