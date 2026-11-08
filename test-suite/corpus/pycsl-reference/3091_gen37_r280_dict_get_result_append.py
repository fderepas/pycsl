r"""Test 3091 — route #280 (expected FAIL): `d.get(0, []).append(1)` — a CALL-RESULT receiver that is
the very list `a` stored in `d` — dropped the receiver; `len(a) == 0` PROVED at 72ab1c57
(red-team p233). CPython: 1. Now refused.
"""
# pycsl-expected: FAIL
from typing import Dict, List


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a: List[int] = []
    d: Dict[int, List[int]] = {0: a}
    d.get(0, []).append(1)
    return len(a)


if __name__ == "__main__":
    assert f() == 1
