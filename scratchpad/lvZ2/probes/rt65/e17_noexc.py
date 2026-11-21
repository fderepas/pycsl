from __future__ import annotations
from pathlib import Path

#@ no_exception \all
#@ ensures \result == 1
#@ assigns \nothing
def f(s: str) -> int:
    c = Path(s).find("a")
    return 1


if __name__ == "__main__":
    print("result", f("a"))
