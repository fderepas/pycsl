from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path


@dataclass
class A:
    p: Path


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    return A(Path(s)) == A(str(Path(s)))


if __name__ == "__main__":
    print("result", f("a"))
