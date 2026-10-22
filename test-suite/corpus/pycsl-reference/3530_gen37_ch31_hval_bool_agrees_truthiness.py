r"""Test 3530 — gen #37 ch31 (expected PASS): `bool(<hval>)` is the definitional `hval_truthy`, the same
function that lowers `if <hval>:`, so `bool(x)` true and `not x` true is unreachable (CPython: 0 for
every input). At 0f7cb454 `bool(<hval>)` was `bool_conv (x: int)`: an L3-tc type error.
"""
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def g(d: Dict[str, PyVal]) -> int:
    x = d.get("t")
    if bool(x):
        if not x:
            return 1
    return 0
