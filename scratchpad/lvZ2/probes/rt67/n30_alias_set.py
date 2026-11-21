from __future__ import annotations
from pathlib import Path
from typing import TypeAlias

Fp: TypeAlias = Path

#@ ensures \result == 1
#@ assigns \nothing
def f(p: Fp) -> int:
    d = {str(p): 1}
    return d.get(p, 0)


if __name__ == "__main__":
    print("result", f(Path("a")))
