# u28 route #565 family probe: q25_str_tuple. CPython f(1) != 0, so `ensures \result == 0` is FALSE.
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    s = None
    if x > 0:
        s, u = "a", 2
    if s is None:
        return 0
    return 1


if __name__ == "__main__":
    print("VIOLATION" if f(1) != 0 else "ok", f(1))
