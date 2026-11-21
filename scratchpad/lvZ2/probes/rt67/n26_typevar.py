from __future__ import annotations
from pathlib import Path
from typing import TypeVar

T = TypeVar("T", bound=Path)

#@ ensures \result == True
#@ assigns \nothing
def f(p: T) -> bool:
    return p == str(p)


if __name__ == "__main__":
    print("result", f(Path("a")))
