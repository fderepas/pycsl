r"""Test 5555 -- gen #37 route #394 (expected FAIL): `set(d.values())` with `d: Dict[str, D]` (D an eq dataclass) (CPython TypeError / ValueError; PROVED at base 3b2d2e763). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: the value's class is derived from its source (or refused as unknown)).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Any, Dict, List, Set, Tuple


@dataclass
class D:
    x: int


#@ no_exception \all
def f(d: Dict[str, D]) -> int:
    s = set(d.values())
    return len(s)


if __name__ == "__main__":
    try:
        print("no violation", f({"a": D(1)}))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
