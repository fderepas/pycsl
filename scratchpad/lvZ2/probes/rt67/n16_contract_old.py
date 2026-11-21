from __future__ import annotations
from pathlib import Path

#@ ensures \result == s
#@ assigns \nothing
def g(s: str) -> str:
    return s


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = Path(s)
    w = g(str(p))
    return w == str(p)
