r"""Test 1555 - ROUTE #161 (gen #29): `math.factorial(-1)` PROVED `no_exception ValueError`; CPython raises ValueError.
"""
# pycsl-expected: FAIL
import math
from typing import List
_ = 0  # anchor


#@ no_exception ValueError
def probe() -> int:
    return math.factorial(-1)

