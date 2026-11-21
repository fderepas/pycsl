from __future__ import annotations
from pathlib import Path

#@ ensures \result == 1
#@ assigns \nothing
def f(s: str) -> int:
    p = Path(s)
    try:
        r = "abc".find(p)
    except Exception:
        return 0
    return 1


if __name__ == "__main__":
    print("result", f("a"))
