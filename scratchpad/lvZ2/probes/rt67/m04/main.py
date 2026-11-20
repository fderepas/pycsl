from __future__ import annotations
from pathlib import Path
from h import Box

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    b = Box(Path(s))
    q = b.p
    return q == str(q)


if __name__ == "__main__":
    print("result", f("a"))
