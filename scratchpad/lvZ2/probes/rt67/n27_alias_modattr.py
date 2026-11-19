from __future__ import annotations
import pathlib
from typing import TypeAlias

Fp: TypeAlias = pathlib.Path

#@ ensures \result == True
#@ assigns \nothing
def f(p: Fp) -> bool:
    return p == str(p)


if __name__ == "__main__":
    print("result", f(pathlib.Path("a")))
