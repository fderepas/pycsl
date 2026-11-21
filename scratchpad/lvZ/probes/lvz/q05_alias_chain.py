from __future__ import annotations
from pathlib import Path
from typing import TypeAlias

A = Path
B: TypeAlias = A


#@ ensures \result == True
def f(p: B) -> bool:
    return p == str(p)


if __name__ == "__main__":
    print("result", f(Path("a")))
