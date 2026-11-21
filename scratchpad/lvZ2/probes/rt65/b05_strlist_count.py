from __future__ import annotations
from pathlib import Path

#@ ensures \result == 1
#@ assigns \nothing
def f(s: str) -> int:
    p = Path(s)
    xs = [str(p)]
    if p in xs:
        return 1
    return 1


if __name__ == "__main__":
    print("result", f("a"))
