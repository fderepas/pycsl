r"""Test 7751 -- route #489 (control, expected PASS): a `\trusted` k reads only the int field `o.v == 0`; ANOTHER class's `__eq__` writes, `C` has no dunder; CPython returns 0
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


class D:
    def __init__(self) -> None:
        self.w = 0

    #@ assigns self.w
    def __eq__(self, x: object) -> bool:
        self.w = 7
        return True


class C:
    def __init__(self) -> None:
        self.v = 0


#@ \trusted
def k(o: C) -> int:
    return 1 if o.v == 0 else 2


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
