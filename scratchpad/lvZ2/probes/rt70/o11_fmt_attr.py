from __future__ import annotations
from pathlib import Path


#@ requires str(p) == "a/b"
#@ ensures \result == "a/b"
#@ assigns \nothing
def f(p: Path) -> str:
    return "{0.name}".format(p)


if __name__ == "__main__":
    print("result", f(Path("a/b")))
