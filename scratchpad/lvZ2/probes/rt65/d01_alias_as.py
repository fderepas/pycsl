from __future__ import annotations
from pathlib import Path as P

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = P(s)
    return p == str(p)


if __name__ == "__main__":
    print("result", f("a"))
