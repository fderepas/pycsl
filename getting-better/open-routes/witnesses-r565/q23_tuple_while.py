# u28 route #565 family probe: q23_tuple_while. CPython f(1) != 0, so `ensures \result == 0` is FALSE.
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    i = 0
    while i < x:
        t, i = i + 7, i + 1
    if t is None:
        return 0
    return 1


if __name__ == "__main__":
    print("VIOLATION" if f(1) != 0 else "ok", f(1))
