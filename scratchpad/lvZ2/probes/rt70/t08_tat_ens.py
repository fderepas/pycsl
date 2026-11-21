from __future__ import annotations
from pathlib import Path
from typing import TypeAliasType

Fp = TypeAliasType("Fp", Path)


#@ ensures \result == p
#@ assigns \nothing
def f(p: Fp) -> str:
    return str(p)


if __name__ == "__main__":
    p = Path("a")
    r = f(p)
    print("result", r == p)
