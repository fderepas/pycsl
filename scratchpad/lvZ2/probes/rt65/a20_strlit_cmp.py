from __future__ import annotations
from pathlib import Path

#@ ensures \result == True
#@ assigns \nothing
def f() -> bool:
    return Path("a") == str(Path("a"))


if __name__ == "__main__":
    print("result", f())
