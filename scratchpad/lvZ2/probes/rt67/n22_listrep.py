from __future__ import annotations
from pathlib import Path

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    ys = [Path(s)] * 1
    return ys[0] == str(ys[0])


if __name__ == "__main__":
    print("result", f("a"))
