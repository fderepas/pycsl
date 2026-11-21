r"""Test 2333 — route #246 (expected PASS): CONTROL. A PROGRAM-side `isinstance(<Any>, int)` on a
rebound name is a fresh value per evaluation, so the body still verifies against a contract that does
not depend on the answer. CPython `f(1)` = 1, `f(1.0)` = 0, both within `0 <= \result <= 1`.
"""
# pycsl-expected: PASS
from typing import Any


#@ ensures 0 <= \result <= 1
#@ assigns \nothing
def f(x: Any) -> int:
    y = x
    if isinstance(y, int):
        return 1
    return 0


if __name__ == "__main__":
    assert f(1) == 1 and f(1.0) == 0
