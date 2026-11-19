r"""Test 7636 -- route #482 (expected FAIL: PROVED at base, REFUSED PYCSL-R482-TRUSTED-FRAME-UNTRACKED): a `\trusted` def stores through `zs = [o.xs]; zs[0][0] = 7`; CPython returns 7.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List


class C:
    def __init__(self) -> None:
        self.xs: List[int] = [0]


#@ \trusted
def k(o: C) -> int:
    zs = [o.xs]
    zs[0][0] = 7
    return 0


#@ ensures \result == 0
def f(n: int) -> int:
    o = C()
    k(o)
    return o.xs[0]


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 0):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
