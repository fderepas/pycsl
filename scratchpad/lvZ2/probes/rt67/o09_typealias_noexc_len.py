from __future__ import annotations
from pathlib import Path
from typing import TypeAlias

Fp: TypeAlias = Path

#@ requires len(str(p)) == 1
#@ ensures \result == 1
#@ no_exception \all
#@ assigns \nothing
def f(p: Fp) -> int:
    return len(p)


if __name__ == "__main__":
    print("result", f(Path("a")))
