r"""Test 7630 -- route #482 (expected FAIL: PROVED at base, REFUSED PYCSL-R482-TRUSTED-FRAME-UNTRACKED): a `\trusted` method with no `assigns` stores through `ys = (self.xs,)[0]`; CPython returns 7.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List


class C:
    def __init__(self) -> None:
        self.xs: List[int] = [0]

    #@ \trusted
    def m(self) -> int:
        ys = (self.xs,)[0]
        ys[0] = 7
        return 0


#@ ensures \result == 0
def f(n: int) -> int:
    c = C()
    c.m()
    return c.xs[0]


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 0):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
