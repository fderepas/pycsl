from __future__ import annotations
from pathlib import Path
import h

#@ ensures \result == 1
#@ assigns \nothing
def f(s: str) -> int:
    a, n = h.pair(Path(s), 3)
    t = str(a)
    if a != t:
        return 0
    return 1


if __name__ == "__main__":
    print("result", f("a"))
