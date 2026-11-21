from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path


@dataclass(order=True)
class A:
    p: Path


#@ requires str(p) == "a/b"
#@ requires str(q) == "a-b"
#@ ensures \result == False
#@ assigns \nothing
def f(p: Path, q: Path) -> bool:
    return A(p) < A(q)


if __name__ == "__main__":
    print("result", f(Path("a/b"), Path("a-b")))
