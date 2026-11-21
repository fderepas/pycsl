from __future__ import annotations
from pathlib import Path

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    return isinstance(Path(s), str)


if __name__ == "__main__":
    print("result", f("a"))
