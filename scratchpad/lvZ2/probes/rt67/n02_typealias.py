from __future__ import annotations
from pathlib import Path
from typing import TypeAlias

PathT: TypeAlias = Path

#@ ensures \result == True
#@ assigns \nothing
def f(p: PathT) -> bool:
    return p == str(p)


if __name__ == "__main__":
    print("result", f(Path("a")))
