from __future__ import annotations
import pathlib

type Fp = pathlib.Path


#@ ensures \result == True
def f(p: Fp) -> bool:
    return p == str(p)


if __name__ == "__main__":
    print("result", f(pathlib.Path("a")))
