r"""Test 2332 — route #246 (expected PASS): CONTROL. Route #239's `requires isinstance(x, T)` -> body
link is kept for a class whose `==` never crosses types: `requires isinstance(x, list)` decides the body
test, so `\result == 1` PROVES (CPython `f([1])` = 1).
"""
# pycsl-expected: PASS
from typing import Any


#@ requires isinstance(x, list)
#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any) -> int:
    if isinstance(x, list):
        return 1
    return 0


if __name__ == "__main__":
    assert f([1]) == 1
