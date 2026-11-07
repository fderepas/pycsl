r"""Test 2242 — route #241 (expected FAIL): a generator ACTUAL to an `Any` parameter was the
LITERAL `0` — `g(v for v in [1])` emitted `g 0` — so `g`'s `ensures x == 0 ==> \result == 1`
discharged `\result == 1` at 1e4b380e while CPython `m()` = 0 (a generator is not `0`). Route
#239 had made the local-binding form fresh; the generator VALUE is now `(any int)` in every
position, so the postcondition is unproved. Control: 2252.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures x == 0 ==> \result == 1
#@ assigns \nothing
def g(x: Any) -> int:
    if x == 0:
        return 1
    return 0


#@ ensures \result == 1
#@ assigns \nothing
def m() -> int:
    return g(v for v in [1])
