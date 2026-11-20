from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

Fp: TypeAlias = Path


@dataclass
class A:
    p: Fp


#@ ensures \result == True
#@ assigns \nothing
def f(a: A) -> bool:
    return a.p == str(a.p)


if __name__ == "__main__":
    print("result", f(A(Path("a"))))
