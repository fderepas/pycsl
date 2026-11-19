# u28 route #565 family probe: q42_optional_walrus_isnone. CPython f(1) != 0, so `ensures \result == 0` is FALSE.
from __future__ import annotations
from typing import Optional


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t: Optional[int] = None
    if (t := x) > 0:
        pass
    if t is None:
        return 0
    return 1


if __name__ == "__main__":
    print("VIOLATION" if f(1) != 0 else "ok", f(1))
