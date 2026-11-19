from __future__ import annotations
from h import P0

#@ ensures \result == True
#@ assigns \nothing
def f() -> bool:
    p = P0
    return p == str(p)


if __name__ == "__main__":
    print("result", f())
