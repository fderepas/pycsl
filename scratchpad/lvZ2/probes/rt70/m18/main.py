from __future__ import annotations
from pathlib import Path
import h

#@ ensures \result == True
#@ assigns \nothing
def f(p: h.Fp) -> bool:
    return p == str(p)


if __name__ == "__main__":
    print("result", f(Path("a")))
