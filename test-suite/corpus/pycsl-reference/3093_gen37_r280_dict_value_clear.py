r"""Test 3093 — route #280 (expected FAIL): `d[0].clear()` under `assigns \nothing` with
`d[0] == \old(d[0])` PROVED at 72ab1c57 (red-team p237). CPython: `d[0]` becomes `[]`. Now refused.
"""
# pycsl-expected: FAIL
from typing import Dict, List


#@ requires 0 in d
#@ ensures d[0] == \old(d[0])
#@ assigns \nothing
def f(d: Dict[int, List[int]]) -> None:
    d[0].clear()


if __name__ == "__main__":
    x: Dict[int, List[int]] = {0: [1]}
    f(x)
    assert x[0] == []
