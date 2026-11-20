from __future__ import annotations
from pathlib import Path


def deco(fn: object) -> object:
    return fn


@deco
#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = Path(s)
    return p == str(p)


if __name__ == "__main__":
    print("result", f("a"))
