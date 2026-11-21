from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path


@dataclass
class A:
    p: Path


@dataclass
class B:
    p: str


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    a = A(Path(s))
    b = B(str(a.p))
    return a.p.__class__ is not str and b.p == str(Path(s))


if __name__ == "__main__":
    print("result", f("a"))
