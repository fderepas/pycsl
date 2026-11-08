r"""Test 2247 — route #241 (expected FAIL): a generator RETURNED from an `Any` function was the
literal `0`, so `ensures \result == 0` PROVED at 1e4b380e while CPython `r() == 0` is False. The
returned value is now `(any int)`; the postcondition is unproved.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def r() -> Any:
    return (v for v in [1])
