r"""Test 1744 — WITNESS: a `Literal[1.5]`.

"only int/str/bool/None literals" — PEP 586 excludes floats from Literal, and PyCSL's
refusal says so by name. Sibling of 1743 (mixed kinds).
"""
# pycsl-expected: FAIL
from typing import Literal

_ = 0  # anchor


#@ requires n >= 0
#@ ensures \result == 0
def f(n: int, m: Literal[1.5]) -> int:
    return 0
