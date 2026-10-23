r"""Test 1751 — WITNESS: a Callable annotation without the bracketed argument list.

PYCSL-TY3-CALLABLE-SCOPE — `Callable[int, int]` omits the argument LIST that PEP 484 requires (`Callable[[int], int]`). One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no file proving it can fire.
"""
# pycsl-expected: FAIL
from typing import Callable

_ = 0  # anchor


#@ requires n >= 0
#@ ensures \result == 0
def f(n: int, g: Callable[int, int]) -> int:
    return 0
