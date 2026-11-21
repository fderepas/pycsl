from __future__ import annotations
import os.path
from pathlib import Path

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = Path(s)
    q = os.path.join(p, "b")
    return q == q
