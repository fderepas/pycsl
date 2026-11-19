from __future__ import annotations
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    from h import keep
    q = keep(Path(s))
    return q == str(Path(s))


if __name__ == "__main__":
    print("result", f("a"))
