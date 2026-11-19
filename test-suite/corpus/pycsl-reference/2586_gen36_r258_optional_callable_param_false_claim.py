r"""Test 2586 — route #258 (expected FAIL): a `Optional[Callable[[int], int]]` parameter was lowered with only its `None` arm
(the other arm was DROPPED, GT1), so `x is not None` was dead and `ensures \result == 5` PROVED for a
body returning 6 on every non-None argument. CPython: `f(abs)` is 6. PROVED at 183c35a2; the annotation now
lowers to the erased `Any` value and the claim is not provable.
"""
# pycsl-expected: FAIL
from typing import Callable, Optional


#@ ensures \result == 5
#@ assigns \nothing
def f(x: Optional[Callable[[int], int]]) -> int:
    if x is not None:
        return 6
    return 5


if __name__ == "__main__":
    assert f(abs) == 6
