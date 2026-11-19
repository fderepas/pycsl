r"""Test 1593 - ROUTE #172 (gen #29): `int("1.5")` caught by `except Exception` PROVED `\result == 0` (CPython 9). Now refused.
"""
# pycsl-expected: FAIL
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    try:
        v = int("1.5")
    except Exception:
        return 9
    return v * 0
