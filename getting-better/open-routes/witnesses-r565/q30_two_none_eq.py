# u28 route #565 family probe: q30_two_none_eq. CPython f(1) != 0, so `ensures \result == 0` is FALSE.
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    u = None
    t, u = 1, x + 1
    if t == u:
        return 0
    return 1


if __name__ == "__main__":
    print("VIOLATION" if f(1) != 0 else "ok", f(1))
