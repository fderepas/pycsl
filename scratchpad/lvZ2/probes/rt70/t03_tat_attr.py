from __future__ import annotations
import typing
from pathlib import Path

Fp = typing.TypeAliasType("Fp", Path)


#@ ensures \result == True
#@ assigns \nothing
def f(p: Fp) -> bool:
    return p == str(p)


if __name__ == "__main__":
    print("result", f(Path("a")))
