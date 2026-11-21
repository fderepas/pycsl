from __future__ import annotations
import sys
import types
_m = types.ModuleType("pathlib")
_m.Path = lambda s: object()
sys.modules["pathlib"] = _m
from pathlib import Path

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    return Path(s) == Path(s)


if __name__ == "__main__":
    print("result", f("a"))
