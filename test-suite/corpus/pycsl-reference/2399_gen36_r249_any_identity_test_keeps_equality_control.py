r"""Test 2399 — route #249 (expected PASS): CONTROL: an identity test is not `==`: `x is x` (route #52's same-name shape) and `x is None` keep
Why3 `=`, so `\result == 1` PROVES for `if x is x: return 1`.
"""
# pycsl-expected: PASS
from typing import Any


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any) -> int:
    if x is x:
        return 1
    return 0


if __name__ == "__main__":
    assert f(float("nan")) == 1 and f(None) == 1
