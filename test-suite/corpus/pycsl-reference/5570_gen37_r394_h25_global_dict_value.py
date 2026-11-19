r"""Test 5570 -- gen #37 route #394 (expected FAIL): `{G["a"]}` with `G = {"a": D(1)}` (CPython TypeError / ValueError; PROVED at base 3b2d2e763). REFUSED (PYCSL-R349-UNHASHABLE-RECORD: the value's class is derived from its source (or refused as unknown)).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class D:
    x: int


G = {"a": D(1)}


#@ no_exception \all
def f() -> int:
    s = {G["a"]}
    return len(s)


if __name__ == "__main__":
    try:
        print("result", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
