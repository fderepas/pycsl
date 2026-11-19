from __future__ import annotations
from pathlib import Path
import pkg.h

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    q = pkg.h.ident(Path(s))
    return q == str(q)


if __name__ == "__main__":
    print("result", f("a"))
