from __future__ import annotations
from h import Fp


#@ ensures \result == True
def f(p: Fp) -> bool:
    return p == str(p)


if __name__ == "__main__":
    from pathlib import Path
    print("result", f(Path("a")))
