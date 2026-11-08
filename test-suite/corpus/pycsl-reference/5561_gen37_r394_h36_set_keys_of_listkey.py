r"""Test 5561 -- gen #37 route #394 (expected FAIL): `set(m.values())` with `m: Dict[str, List[int]]` (CPython TypeError / ValueError; PROVED at base 3b2d2e763). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: the value's class is derived from its source (or refused as unknown)).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class D:
    x: int


#@ no_exception \all
def f(m: Dict[str, List[int]]) -> int:
    s = set(m.values())
    return len(s)


if __name__ == "__main__":
    try:
        print("result", f({"a": [1]}))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
