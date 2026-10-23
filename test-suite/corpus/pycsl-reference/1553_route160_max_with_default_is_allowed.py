r"""Test 1553 - ROUTE #160 control (gen #29): `max([], default=0)` under `no_exception ValueError` is not refused and PROVES.
"""
from typing import List
_ = 0  # anchor


#@ no_exception ValueError
def probe() -> int:
    return max([], default=0)
