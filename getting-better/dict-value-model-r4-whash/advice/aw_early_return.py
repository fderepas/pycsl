r"""W-hash advice audit: witness 9883 with the advice "... or an early `return` when it is not one, with no rebinding in between" followed. Expected: VERIFIES under `no_exception \all`."""
from typing import Any

PyVal = Any


#@ no_exception \all
#@ ensures \result == n + 1
def f(v: PyVal, n: int) -> int:
    if not isinstance(v, str):
        return n + 1
    s = {v}
    return n + 1
