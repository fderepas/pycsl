# u28 side probe: Optional carrier, None bound on the LAST-emitted branch of a join.
from __future__ import annotations
from typing import Optional


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t: Optional[int] = None
    if x > 0:
        t = 5
    else:
        t = None
    if t:
        return 1
    return 0


if __name__ == "__main__":
    print("VIOLATION" if f(1) != 0 else "ok", f(1))
