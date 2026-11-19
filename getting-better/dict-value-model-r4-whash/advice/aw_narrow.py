r"""W-hash advice audit: witness 9883 with the advice "Narrow it first (`if isinstance(v, str):` around the site ...)" followed. Expected: VERIFIES under `no_exception \all`."""
from typing import Any

PyVal = Any


#@ no_exception \all
#@ ensures \result == n + 1
def f(v: PyVal, n: int) -> int:
    if isinstance(v, str):
        s = {v}
    return n + 1
