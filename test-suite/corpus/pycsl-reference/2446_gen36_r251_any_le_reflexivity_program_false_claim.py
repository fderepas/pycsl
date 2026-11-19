r"""Test 2446 — route #251 (expected FAIL): Program side: `if x <= x` was decided True on `x: Any`, so `\result == 0`
PROVED. CPython: `f(float("nan"))` is 1 — no user class needed.
PROVED at aaf9b355.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    if x <= x:
        return 0
    return 1


if __name__ == "__main__":
    assert f(float("nan")) == 1
