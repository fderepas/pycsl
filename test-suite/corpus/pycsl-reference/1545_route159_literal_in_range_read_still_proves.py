r"""Test 1545 - ROUTE #159 control (gen #29): `[1, 2][1]` under `no_exception IndexError` PROVES on both sides.
"""
from typing import List
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    xs: List[int] = [1, 2]
    return xs[1]
