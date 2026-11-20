from __future__ import annotations
from pathlib import Path

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    g = lambda: Path(s)
    p = g()
    return p == str(p)


if __name__ == "__main__":
    print("result", f("a"))
