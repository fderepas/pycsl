r"""Test 7612 -- route #486 control (expected PASS) under `--memory-model typed`: `a[0] += 1` on `a: List[int]` (an int element: a faithful element update). PROVED at base 0c61bfc3f and at the repair.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model typed
from typing import List

#@ requires len(a) == 1
#@ ensures a[0] == \old(a[0]) + 1
#@ assigns a[0]
def f(a: List[int]) -> int:
    a[0] += 1
    return 0
