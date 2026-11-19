r"""Test 1589 - ROUTE #171 (gen #29): `try: v = int("1.5") except ValueError: return 9; return v * 0` PROVED `\result == 0` (CPython 9): `int(<str>)` is an opaque `str_to_int` that never raises. Now refused (no faithful obligation, route #66).
"""
# pycsl-expected: FAIL
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    try:
        v = int("1.5")
    except ValueError:
        return 9
    return v * 0
