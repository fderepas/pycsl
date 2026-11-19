from __future__ import annotations
from pathlib import Path
from h import keep

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    q = keep(Path(s))
    return q == str(Path(s))


if __name__ == "__main__":
    print("result", f("a"))
