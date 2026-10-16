r"""Test 2272 — route #242 (expected FAIL): `r()` returns a generator, an erased value lowered to a
fresh `(any int)`; inside the `let function r () = (any int)` Why3 fixed it once, so `r() == r()`
PROVED `\result == 1` at f0fc0201. CPython compares two distinct generator objects: `m()` = 0. `r`
is now a plain `let` (two calls, two unknown values): unproved.
"""
# pycsl-expected: FAIL
from typing import Any


#@ assigns \nothing
def r() -> Any:
    return (v for v in [1])


#@ ensures \result == 1
#@ assigns \nothing
def m() -> int:
    if r() == r():
        return 1
    return 0
