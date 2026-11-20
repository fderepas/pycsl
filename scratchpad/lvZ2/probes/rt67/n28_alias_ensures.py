from __future__ import annotations
from pathlib import Path
from typing import TypeAlias

Fp: TypeAlias = Path

#@ ensures \result == p
#@ assigns \nothing
def g(p: Fp) -> str:
    return str(p)


if __name__ == "__main__":
    r = g(Path("a"))
    print("result", repr(r), "ensures(\\result == p):", r == Path("a"))
