r"""Test 7822 -- route #493 (control, expected PASS): a `\trusted` `__init__` of another class K stores `self.r = len(o)` -- now JUDGED as a bodyless val -- and C's only dunder `__len__` is `#@ assigns \nothing`; f calls `K(o)`; CPython returns 0
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns \nothing
    def __len__(self) -> int:
        return 1


class K:
    #@ \trusted
    def __init__(self, o: C) -> None:
        self.r = len(o)


#@ ensures \result == 0
def f(n: int) -> int:
    o = C()
    K(o)
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
