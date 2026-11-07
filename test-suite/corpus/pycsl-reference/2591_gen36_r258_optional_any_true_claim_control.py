r"""Test 2591 — route #258 (expected PASS): CONTROL: an `Optional[Any]` parameter (now the erased `Any`
value) still proves a TRUE claim over both branches of `x is not None`.
"""
# pycsl-expected: PASS
from typing import Any, Optional


#@ ensures \result == 5 or \result == 6
#@ assigns \nothing
def f(x: Optional[Any]) -> int:
    if x is not None:
        return 6
    return 5


if __name__ == "__main__":
    assert f(1) == 6 and f(None) == 5
