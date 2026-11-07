# u28 route #565 family probe: q19_tuple_eq0. CPython f(1) != 0, so `ensures \result == 0` is FALSE.
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    t, u = 0, 2
    if t == 0:
        return 1
    return 0


if __name__ == "__main__":
    print("VIOLATION" if f(1) != 0 else "ok", f(1))
