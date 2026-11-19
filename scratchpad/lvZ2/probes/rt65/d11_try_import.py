from __future__ import annotations
try:
    from pathlib import Path
except ImportError:
    pass

#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = Path(s)
    return p == str(p)


if __name__ == "__main__":
    print("result", f("a"))
