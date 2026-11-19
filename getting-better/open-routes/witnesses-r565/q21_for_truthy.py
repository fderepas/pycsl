# u28 route #565 family probe: q21_for_truthy. CPython f(1) != 0, so `ensures \result == 0` is FALSE.
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    for t in [5]:
        pass
    if not t:
        return 0
    return 1


if __name__ == "__main__":
    print("VIOLATION" if f(1) != 0 else "ok", f(1))
