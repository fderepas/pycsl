r"""Test 1532 - ROUTE #157 (gen #29): `a[0:1] = [7, 8]` blitted ONE element (`a` stayed `[7, 2]`) and `a[1] != 8` PROVED; CPython `[7, 8, 2]`, so 8.
"""
# pycsl-expected: FAIL
from typing import List
_ = 0  # anchor


#@ ensures \result != 8
def probe() -> int:
    a: List[int] = [1, 2]
    a[0:1] = [7, 8]
    return a[1]

