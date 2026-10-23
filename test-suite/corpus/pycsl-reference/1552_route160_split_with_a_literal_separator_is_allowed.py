r"""Test 1552 - ROUTE #160 control (gen #29): `s.split(" ")` under `no_exception ValueError` is not refused and PROVES.
"""
from typing import List
_ = 0  # anchor


#@ no_exception ValueError
def probe() -> int:
    s = "a b"
    return len(s.split(" "))
