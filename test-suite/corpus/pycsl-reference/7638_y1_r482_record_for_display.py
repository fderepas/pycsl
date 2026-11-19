r"""Test 7638 -- route #482 (expected FAIL: PROVED at base, REFUSED PYCSL-R482-TRUSTED-FRAME-UNTRACKED): a `\trusted` def stores through `for p in [o]`; CPython returns 7.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List


class C:
    def __init__(self) -> None:
        self.v = 0
        self.xs: List[int] = [0]


#@ \trusted
def k(o: C) -> int:
    for p in [o]:
        p.v = 7
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
