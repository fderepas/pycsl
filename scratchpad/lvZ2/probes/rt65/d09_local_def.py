from __future__ import annotations
from pathlib import Path

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    def Path(x: str) -> object:
        return object()
    return Path(s) == Path(s)


if __name__ == "__main__":
    print("result", f("a"))
