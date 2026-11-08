r"""Test 7737 -- route #489 (expected FAIL: PROVED at base, REFUSED PYCSL-R489-IMPLICIT-DUNDER (store model)): an IMPORTED un-marked `k(o)` reads `len(o)` (multi_file_lib/u1_h489a.py); `C.__len__` writes `self.v`; CPython returns 7
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model store
from typing import Any, Dict, List, Optional


from multi_file_lib.u1_h489a import C, k


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
