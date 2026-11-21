from __future__ import annotations
import os
from pathlib import Path

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = Path(s)
    return os.path.exists(p) == os.path.exists(str(p))


if __name__ == "__main__":
    print("result", f("/etc"))
