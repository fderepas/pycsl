from __future__ import annotations
from pathlib import Path

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    t = (Path(s),) * 1
    return t == (str(Path(s)),)


if __name__ == "__main__":
    print("result", f("a"))
