r"""Test 1604 - ROUTE #173 carrier (gen #29): `for a, b in ["abc"]` under `#@ no_exception ValueError` PROVED (CPython: too many values to unpack). A tuple loop target is now accepted only over enumerate / zip / .items() of matching arity.
"""
# pycsl-expected: FAIL
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    words: List[str] = ["abc"]
    for a, b in words:
        pass
    return 0
