from __future__ import annotations
from pathlib import Path

#@ ensures \result == True
#@ assigns \nothing
def f(p: Path) -> bool:
    return p == str(p)


if __name__ == "__main__":
    print("result", f(Path("a")))
