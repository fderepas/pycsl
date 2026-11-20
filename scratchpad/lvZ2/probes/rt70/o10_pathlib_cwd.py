from __future__ import annotations
import pathlib


#@ ensures \result == True
#@ assigns \nothing
def f() -> bool:
    p = pathlib.Path.cwd()
    return p == str(p)


if __name__ == "__main__":
    print("result", f())
