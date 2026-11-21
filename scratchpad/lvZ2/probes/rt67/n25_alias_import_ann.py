from __future__ import annotations
from pathlib import Path as Fp

#@ ensures \result == True
#@ assigns \nothing
def f(p: Fp) -> bool:
    return p == str(p)


if __name__ == "__main__":
    print("result", f(Fp("a")))
