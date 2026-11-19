from __future__ import annotations
from pathlib import Path
from typing import Iterator


#@ assigns \nothing
def gen(s: str) -> Iterator[Path]:
    yield Path(s)


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    for q in gen(s):
        return q == str(q)
    return True


if __name__ == "__main__":
    print("result", f("a"))
