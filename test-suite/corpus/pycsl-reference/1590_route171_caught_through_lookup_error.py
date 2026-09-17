r"""Test 1590 - ROUTE #171 carrier (gen #29): the placeholder-array read caught through the base class `except LookupError` PROVED `\result == 0` (CPython 9).
"""
# pycsl-expected: FAIL
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = []
    try:
        v = xs[0]
    except LookupError:
        return 9
    return v * 0
