r"""Test 7639 -- route #482 (expected FAIL: PROVED at base, REFUSED PYCSL-R482-TRUSTED-FRAME-UNTRACKED): a `\trusted` def stores through `zs = [ys]; zs[0][0] = 7` with `ys = xs` (also route #468's length rule); CPython returns 7.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List


#@ \trusted
def k(xs: List[int]) -> int:
    ys = xs
    zs = [ys]
    ys = [0]
    zs[0][0] = 7
    return 0


#@ requires len(xs) >= 1 and xs[0] == 0
#@ ensures \result == 0
def f(xs: List[int]) -> int:
    k(xs)
    return xs[0]


if __name__ == "__main__":
    try:
        r = f([0])
        if not (r == 0):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
