from __future__ import annotations
from pathlib import Path
from typing import TypeAliasType

Fp = TypeAliasType("Fp", Path)


#@ requires str(p) == "a/b"
#@ requires str(q) == "a-b"
#@ ensures \result == False
#@ assigns \nothing
def f(p: Fp, q: Fp) -> bool:
    return p < q


if __name__ == "__main__":
    print("result", f(Path("a/b"), Path("a-b")))
