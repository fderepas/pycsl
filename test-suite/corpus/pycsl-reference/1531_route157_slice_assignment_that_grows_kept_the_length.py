r"""Test 1531 - ROUTE #157 (gen #29): `a = [1, 2]; a[2:] = [3, 4]` is a RESIZE in Python, but the model is a fixed-length `Array.blit` of `len(a) - 2 = 0` elements, so `len(a) != 4` PROVED; CPython 4. Equal source and slice length is now a proof obligation.
"""
# pycsl-expected: FAIL
from typing import List
_ = 0  # anchor


#@ ensures \result != 4
def probe() -> int:
    a: List[int] = [1, 2]
    a[2:] = [3, 4]
    return len(a)

