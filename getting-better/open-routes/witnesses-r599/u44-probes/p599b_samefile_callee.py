from __future__ import annotations
import os


#@ ensures True
#@ assigns \nothing
def g(s: str) -> int:
    return os.path.getsize(s)


#@ ensures \result == 0
#@ assigns \nothing
def f(s: str, n: int) -> int:
    x = 0
    try:
        if n > 100:
            raise OSError("u")
        x = 1
        k = g(s)
    except OSError:
        return x
    return 0


if __name__ == "__main__":
    r = f("/no/such/u44", 0)
    print("VIOLATION contract" if r != 0 else "result", r)
