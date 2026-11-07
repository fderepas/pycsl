r"""Test 7824 -- route #494 (control, expected PASS): a `\trusted` k returns `o.get() + 1` where `C.get` returns an int; CPython returns 0
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns self.v
    def __len__(self) -> int:
        self.v = 7
        return 1

    def get(self) -> int:
        return self.v


#@ \trusted
def k(o: C) -> int:
    return o.get() + 1


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
