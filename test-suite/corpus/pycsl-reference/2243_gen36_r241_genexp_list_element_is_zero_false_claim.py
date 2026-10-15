r"""Test 2243 — route #241 (expected FAIL): a generator stored as a LIST ELEMENT was the literal
`0` (`Array.make 1 (0)`), so `xs[0] == 0` was decided and `\result == 1` PROVED at 1e4b380e
while CPython `m()` = 0. The element is now `(any int)`; the postcondition is unproved.
"""
# pycsl-expected: FAIL
from typing import Any, List


#@ ensures \result == 1
#@ assigns \nothing
def m() -> int:
    xs: List[Any] = [(v for v in [1])]
    if xs[0] == 0:
        return 1
    return 0
