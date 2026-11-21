from __future__ import annotations
from pathlib import Path
from typing import TypeAlias

Fp: TypeAlias = Path

#@ ensures \result == True
#@ assigns \nothing
def f(p: Fp) -> bool:
    return p in [str(p)]


if __name__ == "__main__":
    print("result", f(Path("a")))
