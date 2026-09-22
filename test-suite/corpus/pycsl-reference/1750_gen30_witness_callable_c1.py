r"""Test 1750 — WITNESS: a Callable whose argument or return type is `Any`.

PYCSL-TY3-GT1 — `Any` in a Callable position is the type the model cannot narrow, so it is refused rather than guessed. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no file proving it can fire.
"""
# pycsl-expected: FAIL
from typing import Callable

_ = 0  # anchor


#@ requires n >= 0
#@ ensures \result == 0
def f(n: int, g: Callable[[int], Any]) -> int:
    return 0
