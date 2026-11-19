r"""Test 1551 - ROUTE #160 control (gen #29): `range(0, 5, 2)` under `no_exception ValueError` is not refused and PROVES.
"""
from typing import List
_ = 0  # anchor


#@ no_exception ValueError
def probe() -> int:
    t = 0
    for i in range(0, 5, 2):
        t = t + 1
    return t
