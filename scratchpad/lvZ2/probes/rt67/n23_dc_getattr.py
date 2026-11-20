from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Box:
    p: Path


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    b = Box(Path(s))
    q = getattr(b, "p")
    return q == str(q)


if __name__ == "__main__":
    print("result", f("a"))
