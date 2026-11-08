r"""Test 3098 — route #280 (expected FAIL): `d[0].append(1)` where `d[0]` IS the local list `a`;
`len(a) == 0` PROVED at 72ab1c57 (red-team p223). CPython: 1. Now refused.
"""
# pycsl-expected: FAIL
from typing import Dict, List


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a: List[int] = []
    d: Dict[int, List[int]] = {0: a}
    d[0].append(1)
    return len(a)


if __name__ == "__main__":
    assert f() == 1
