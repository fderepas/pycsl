r"""Test 3089 — route #280 (expected FAIL): `d[0].append(1)` on a COMPUTED (subscript) receiver was
lowered to a receiver-less `append_1 1`, so `#@ assigns \nothing` and
`len(d[0]) == \old(len(d[0]))` PROVED at 72ab1c57 (red-team p228). CPython: the length grows.
Now refused (PYCSL-M6-MUTATOR-ON-COMPUTED-RECEIVER).
"""
# pycsl-expected: FAIL
from typing import Dict, List


#@ requires 0 in d
#@ ensures len(d[0]) == \old(len(d[0]))
#@ assigns \nothing
def f(d: Dict[int, List[int]]) -> None:
    d[0].append(1)


if __name__ == "__main__":
    x: Dict[int, List[int]] = {0: []}
    f(x)
    assert len(x[0]) == 1
