r"""Test 2587 — route #258 (expected FAIL): a `Optional[foo]` parameter was lowered with only its `None` arm
(the other arm was DROPPED, GT1), so `x is not None` was dead and `ensures \result == 5` PROVED for a
body returning 6 on every non-None argument. CPython: `f(foo())` is 6. PROVED at 183c35a2; the annotation now
lowers to the erased `Any` value and the claim is not provable.
"""
# pycsl-expected: FAIL
from typing import Optional


class foo:
    pass


#@ ensures \result == 5
#@ assigns \nothing
def f(x: Optional[foo]) -> int:
    if x is not None:
        return 6
    return 5


if __name__ == "__main__":
    assert f(foo()) == 6
