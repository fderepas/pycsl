from __future__ import annotations
from pathlib import Path
from typing import TypeAlias

Fp: TypeAlias = Path

#@ ensures \result == 1
#@ assigns \nothing
def f(p: Fp) -> int:
    t = str(p)
    if p != t:
        return 0
    return 1


if __name__ == "__main__":
    print("result", f(Path("a")))
