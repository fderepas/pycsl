from __future__ import annotations
import hashlib
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def f(s: str, t: str) -> bool:
    p = Path(s)
    q = Path(t)
    if s == t:
        return p == q
    return True


if __name__ == "__main__":
    print("result", f("a", "a"))
