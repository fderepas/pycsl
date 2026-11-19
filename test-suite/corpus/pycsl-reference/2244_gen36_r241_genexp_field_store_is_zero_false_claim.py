r"""Test 2244 — route #241 (expected FAIL): a generator stored into an `Any` FIELD was the literal
`0` (`c.x <- 0`), so `c.x == 0` was decided and `\result == 1` PROVED at 1e4b380e while CPython
`m()` = 0. The stored value is now `(any int)`; the postcondition is unproved.
"""
# pycsl-expected: FAIL
from typing import Any


class C:
    def __init__(self) -> None:
        self.x: Any = 5


#@ ensures \result == 1
#@ assigns \nothing
def m() -> int:
    c = C()
    c.x = (v for v in [1])
    if c.x == 0:
        return 1
    return 0
