r"""Test 1544 - ROUTE #159 control (gen #29): `xs = []; xs.append(7); xs[0]` under `no_exception IndexError` discharges the new Seq bound and PROVES on both sides.
"""
from typing import List
_ = 0  # anchor


#@ no_exception IndexError
def probe() -> int:
    xs: List[int] = []
    xs.append(7)
    return xs[0]
