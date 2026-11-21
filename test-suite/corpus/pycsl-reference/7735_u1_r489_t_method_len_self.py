r"""Test 7735 -- route #489 (expected FAIL: PROVED at base, REFUSED PYCSL-R489-IMPLICIT-DUNDER): a `\trusted` method reads `len(self)`; `C.__len__` writes `self.v`; CPython returns 7
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ \trusted
    def m(self) -> int:
        return len(self)

    #@ assigns self.v
    def __len__(self) -> int:
        self.v = 7
        return 1


#@ ensures \result == 0
def f(n: int) -> int:
    o = C()
    o.m()
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
