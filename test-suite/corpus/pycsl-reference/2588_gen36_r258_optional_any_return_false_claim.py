r"""Test 2588 — route #258 (expected FAIL): a `-> Optional[Any]` RETURN annotation was lowered with only
its `None` arm (GT1 drop), so `return y` did not even type-check (L3-tc, fail-closed at 183c35a2). The
return now lowers to the erased `Any` value: the file type-checks and the caller's false claim
`\result == 5` is not provable. CPython: `f()` is 6.
"""
# pycsl-expected: FAIL
from typing import Any, Optional


#@ assigns \nothing
def g(y: int) -> Optional[Any]:
    return y


#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    x = g(3)
    if x is not None:
        return 6
    return 5


if __name__ == "__main__":
    assert f() == 6
