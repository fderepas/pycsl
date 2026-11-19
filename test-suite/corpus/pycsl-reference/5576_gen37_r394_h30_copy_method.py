r"""Test 5576 -- gen #37 route #394 (expected FAIL): `b = copy.copy(a); {b}` with `a: D` (CPython TypeError / ValueError; PROVED at base 3b2d2e763). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: the value's class is derived from its source (or refused as unknown)).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class D:
    x: int


import copy


#@ no_exception \all
def f(a: D) -> int:
    b = copy.copy(a)
    s = {b}
    return len(s)


if __name__ == "__main__":
    try:
        print("result", f(D(1)))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
