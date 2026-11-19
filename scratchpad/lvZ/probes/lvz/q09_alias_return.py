from __future__ import annotations
from pathlib import Path
from typing import TypeAlias

Fp: TypeAlias = Path


def mk(s: str) -> Fp:
    return Path(s)


#@ ensures \result == True
def f(s: str) -> bool:
    p = mk(s)
    return p == str(p)


if __name__ == "__main__":
    print("result", f("a"))
