from __future__ import annotations
from pathlib import Path
from typing import TypeAlias

Fp: TypeAlias = Path

#@ requires p == "a"
#@ ensures \result == 1
#@ assigns \nothing
def f(p: Fp) -> int:
    if str(p) == "a":
        return 1
    return 0


if __name__ == "__main__":
    print("result", f(Path("b")))
