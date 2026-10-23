r"""Test 1349 — ROUTE #127: `__builtins__.len = seven` (no import needed) rebinds the builtin `len`; `len([1, 2])` PROVED `\result == 2` while CPython (run as a script, where `__builtins__` is the module) returns 7. `__builtins__` is now an object root of the rebinding refusal.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List


def seven(xs: List[int]) -> int:
    return 7


__builtins__.len = seven


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2]
    return len(xs)
