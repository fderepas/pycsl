r"""Test 7752 -- route #489 (control, expected PASS): a `\trusted` k computes `max(o, C())` (rt41 d13006): only the OTHER item's verified `__gt__` (frame `self.v`) runs, with `o` as its argument; CPython returns 0
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns self.v
    def __gt__(self, x: 'C') -> bool:
        self.v = 7
        return True


#@ \trusted
def k(o: C) -> int:
    p = max(o, C())
    return 0


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
