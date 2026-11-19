r"""Test 1377 — ROUTE #134: route #116's `pick("inc")(3)` resolver requires `_g = globals()` bound exactly once, and counted that over the module's TOP-LEVEL statements only; `if True: _g = {"inc": dec}` rebinds it inside a compound statement, and `g()` was lowered to `(inc 3)` and PROVED `\result == 4` while CPython calls `dec` and returns 2. A single-binding module name bound again anywhere in module scope is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Any

_g = globals()


#@ ensures \result == y + 1
#@ assigns \nothing
def inc(y: int) -> int:
    return y + 1


#@ ensures \result == y - 1
#@ assigns \nothing
def dec(y: int) -> int:
    return y - 1


if True:
    _g = {"inc": dec}


#@ \trusted
def pick(name: str) -> Any:
    return _g[name]


#@ ensures \result == 4
#@ assigns \nothing
def g() -> int:
    return pick("inc")(3)
