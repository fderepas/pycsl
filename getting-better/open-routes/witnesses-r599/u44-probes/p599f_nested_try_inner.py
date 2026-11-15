from __future__ import annotations
import os
from pathlib import Path


#@ ensures \result == 0
#@ assigns \nothing
def f(s: str) -> int:
    x = 0
    try:
        Path.cwd()
        x = 1
        if len(s) >= 0:
            k = os.path.getsize(s)
    except OSError:
        return x
    return 0


if __name__ == "__main__":
    r = f("/no/such/u44")
    print("VIOLATION contract" if r != 0 else "result", r)
