from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Box:
    p: Path


#@ ensures \result == 1
#@ assigns \nothing
def f(s: str) -> int:
    b = Box(Path(s))
    match b:
        case Box(p=q):
            if q == str(q):
                return 1
            return 0
    return 1


if __name__ == "__main__":
    print("result", f("a"))
