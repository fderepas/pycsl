# u28 route #565 family probe: q11_augassign_nan. CPython f(1) != 0, so `ensures \result == 0` is FALSE.
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = float("nan")
    t, u = 1.0, 2.0
    if t == t:
        return 1
    return 0


if __name__ == "__main__":
    print("VIOLATION" if f(1) != 0 else "ok", f(1))
