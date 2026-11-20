from __future__ import annotations
import os
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def f(x: os.PathLike) -> bool:
    q = Path(x)
    return q == str(q)


class K:
    def __fspath__(self) -> str:
        return "a"


if __name__ == "__main__":
    print("result", f(K()))
