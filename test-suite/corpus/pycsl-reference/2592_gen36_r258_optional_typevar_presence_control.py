r"""Test 2592 — route #258 (expected FAIL): CONTROL: an `Optional[T]` (TypeVar) parameter keeps its
two-armed variant with an opaque payload (relaunch #17), so `x is not None` is live and the FALSE claim
`\result == 5` is not provable, before and after the repair. CPython: `f(1)` is 6.
"""
# pycsl-expected: FAIL
from typing import Optional, TypeVar

T = TypeVar("T")


#@ ensures \result == 5
#@ assigns \nothing
def f(x: Optional[T]) -> int:
    if x is not None:
        return 6
    return 5


if __name__ == "__main__":
    assert f(1) == 6
