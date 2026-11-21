r"""Test 7820 -- route #491 (control, expected PASS): a `\trusted` k computes `len([1] * o.v)` -- the repetition count is the int FIELD, not the record (C's `__index__` / `__len__` write `self.v` and never run); CPython returns 0
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns self.v
    def __index__(self) -> int:
        self.v = 7
        return 1

    #@ assigns self.v
    def __len__(self) -> int:
        self.v = 7
        return 1


#@ \trusted
def k(o: C) -> int:
    return len([1] * o.v)


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
