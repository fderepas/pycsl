r"""Test 1605 - ROUTE #173 carrier (gen #29): `for k, v, w in d.items()` under `#@ no_exception ValueError` PROVED (CPython: not enough values to unpack).
"""
# pycsl-expected: FAIL
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    for k, v, w in d.items():
        pass
    return 0
