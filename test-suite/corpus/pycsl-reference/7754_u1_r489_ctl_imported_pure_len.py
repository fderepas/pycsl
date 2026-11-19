r"""Test 7754 -- route #489 (control, expected PASS): an IMPORTED un-marked `k(o)` reads `len(o)` (multi_file_lib/u1_h489c.py) where `C.__len__` declares `#@ assigns \nothing`; CPython returns 0
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


from multi_file_lib.u1_h489c import C, k


#@ ensures \result == 0
def f(n: int) -> int:
    o = C()
    k(o)
    return o.v


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 0):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
