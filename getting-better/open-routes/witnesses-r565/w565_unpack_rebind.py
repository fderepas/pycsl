# side probe (lvC): is `t is None` folded after a tuple-unpack rebinding of a None-initialised local?
# CPython: f(1) == 1, so `\result == 0` is FALSE and must not prove.
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    u = None
    if x > 0:
        t, u = 1, 2
    if t is None:
        return 0
    return 1


if __name__ == "__main__":
    print("VIOLATION contract" if f(1) != 0 else "result", f(1))
