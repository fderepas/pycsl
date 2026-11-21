# u28 route #565 family probe: q40_optional_tuple_truthy. CPython f(1) != 0, so `ensures \result == 0` is FALSE.
from __future__ import annotations
from typing import Optional


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t: Optional[int] = None
    t, u = 5, 2
    if t:
        return 1
    return 0


if __name__ == "__main__":
    print("VIOLATION" if f(1) != 0 else "ok", f(1))
