from __future__ import annotations
from typing import Optional
from pathlib import Path

#@ ensures \result == 1
#@ assigns \nothing
def f(s: Optional[str]) -> int:
    try:
        p = Path(s)
        return 1
    except TypeError:
        return 0


if __name__ == "__main__":
    print("result", f(None))
