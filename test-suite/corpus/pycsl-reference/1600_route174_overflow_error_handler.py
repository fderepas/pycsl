r"""Test 1600 - ROUTE #174 (gen #29): `try: f = float(10 ** 400) except OverflowError: return 9; return 0` PROVED `\result == 0` (CPython 9).
"""
# pycsl-expected: FAIL
from typing import List, Dict, Optional
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    try:
        f = float(10 ** 400)
    except OverflowError:
        return 9
    return 0
