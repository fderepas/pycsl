from __future__ import annotations
import pathlib
pathlib.Path = lambda s: object()
from pathlib import Path

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    return Path(s) == Path(s)


if __name__ == "__main__":
    print("result", f("a"))
