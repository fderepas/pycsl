from __future__ import annotations
from pathlib import Path


class MyP(Path):
    pass


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    q = MyP(s)
    return q == str(q)


if __name__ == "__main__":
    print("result", f("a"))
