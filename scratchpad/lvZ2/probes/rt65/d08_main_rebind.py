from __future__ import annotations
from pathlib import Path

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    return Path(s) == Path(s)


if __name__ == "__main__":
    Path = lambda s: object()
    print("result", f("a"))
