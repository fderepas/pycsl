from __future__ import annotations
from pathlib import Path
from typing import List

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    xs = [Path(s)]
    ys = xs * 1
    zs = [str(Path(s))]
    return ys == zs


if __name__ == "__main__":
    print("result", f("a"))
