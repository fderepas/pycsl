from __future__ import annotations
from pathlib import Path


class S(str):
    pass


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = Path(s)
    t = S(str(p))
    return t == p


if __name__ == "__main__":
    print("result", f("a"))
