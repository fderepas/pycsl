r"""Test 1601 - ROUTE #174 (gen #29): `try: s = bytes([255]).decode("utf-8") except UnicodeDecodeError: return 9; return 0` PROVED `\result == 0` (CPython 9).
"""
# pycsl-expected: FAIL
from typing import List, Dict, Optional
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    b = bytes([255])
    try:
        s = b.decode("utf-8")
    except UnicodeDecodeError:
        return 9
    return 0
