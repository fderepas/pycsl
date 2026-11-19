from __future__ import annotations
from pathlib import Path
from h import Box

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    q = Box.keep(Path(s))
    return q == str(Path(s))


if __name__ == "__main__":
    print("result", f("a"))
