from __future__ import annotations
from pathlib import Path
from typing import NewType

MyP = NewType("MyP", Path)

#@ ensures \result == True
#@ assigns \nothing
def f(p: MyP) -> bool:
    return p == str(p)


if __name__ == "__main__":
    print("result", f(MyP(Path("a"))))
