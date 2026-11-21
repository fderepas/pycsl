from __future__ import annotations
from contextlib import nullcontext
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    with nullcontext(Path(s)) as q:
        return q == str(q)


if __name__ == "__main__":
    print("result", f("a"))
