r"""Test 7736 -- route #489 (expected FAIL: PROVED at base, REFUSED PYCSL-R489-IMPLICIT-DUNDER): under --memory-model typed, a `\trusted` k reads `len(o)`; the `\trusted` `C.__len__` declares `assigns self.v`; CPython returns 7
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model typed
from typing import Any, Dict, List, Optional


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ \trusted
    #@ assigns self.v
    def __len__(self) -> int:
        self.v = 7
        return 1


#@ \trusted
def k(o: C) -> int:
    return len(o)


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
