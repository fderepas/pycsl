from __future__ import annotations
from pathlib import Path
from h import name_of


#@ ensures \result == True
def f(s: str) -> bool:
    n = name_of(Path(s))
    return n == n


if __name__ == "__main__":
    print("result", f("a/b"))
