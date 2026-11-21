from __future__ import annotations
from pathlib import Path

#@ ensures \result == 1
#@ assigns \nothing
def f(s: str) -> int:
    p = Path(s)
    d = {str(p): 1}
    return d.get(p, 0)


if __name__ == "__main__":
    print("result", f("a"))
