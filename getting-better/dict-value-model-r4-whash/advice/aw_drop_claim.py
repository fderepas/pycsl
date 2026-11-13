r"""W-hash advice audit: witness 9883 with the advice "or drop the claim" followed (no `no_exception`). Expected: VERIFIES (the hash TypeError is ambient)."""
from typing import Any

PyVal = Any


#@ ensures \result == n + 1
def f(v: PyVal, n: int) -> int:
    if isinstance(v, str):
        n = n + 0
    s = {v}
    return n + 1
