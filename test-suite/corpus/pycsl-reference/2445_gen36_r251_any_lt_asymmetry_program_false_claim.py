r"""Test 2445 — route #251 (expected FAIL): Program side: `if x < y and y < x: return 1` was decided unreachable on two
`Any` parameters (integer `<` is asymmetric), so `\result == 0` PROVED. CPython: `__lt__ -> True`.
PROVED at aaf9b355.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    if x < y and y < x:
        return 1
    return 0


if __name__ == "__main__":
    class P:
        def __lt__(self, o: object) -> bool:
            return True

    assert f(P(), P()) == 1
