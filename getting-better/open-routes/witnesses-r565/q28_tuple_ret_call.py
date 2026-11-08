# u28 route #565 family probe: q28_tuple_ret_call. CPython f(1) != 0, so `ensures \result == 0` is FALSE.
from __future__ import annotations


#@ assigns \nothing
def pair(x: int) -> tuple[int, int]:
    return (x, 2)

#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    t, u = pair(x)
    if t is None:
        return 0
    return 1


if __name__ == "__main__":
    print("VIOLATION" if f(1) != 0 else "ok", f(1))
