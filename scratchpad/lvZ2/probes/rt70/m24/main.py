from __future__ import annotations
from pathlib import Path
from h import ident

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    q = ident(Path(s))
    return q == str(q)


if __name__ == "__main__":
    print("result", f("a"))
