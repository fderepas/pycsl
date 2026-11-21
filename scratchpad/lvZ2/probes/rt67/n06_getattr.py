from __future__ import annotations
from pathlib import Path


class Box:
    #@ assigns \nothing
    def __init__(self, s: str) -> None:
        self.p = Path(s)


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    b = Box(s)
    q = getattr(b, "p")
    return q == str(q)


if __name__ == "__main__":
    print("result", f("a"))
