r"""Test 1752 — WITNESS: a Callable whose argument type is itself generic.

PYCSL-TY3-CALLABLE-SCOPE — a nested generic in a Callable position has no lowering today. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no file proving it can fire.
"""
# pycsl-expected: FAIL
from typing import Callable, List

_ = 0  # anchor


#@ requires n >= 0
#@ ensures \result == 0
def f(n: int, g: Callable[[List[int]], int]) -> int:
    return 0
