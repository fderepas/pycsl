r"""Test 1547 - ROUTE #160 (gen #29): `for i in range(0, 5, 0)` under `no_exception ValueError` PROVED; CPython raises ValueError (zero step). Refused unless the step is a nonzero literal.
"""
# pycsl-expected: FAIL
from typing import List
_ = 0  # anchor


#@ no_exception ValueError
def probe() -> int:
    t = 0
    for i in range(0, 5, 0):
        t = t + 1
    return t

