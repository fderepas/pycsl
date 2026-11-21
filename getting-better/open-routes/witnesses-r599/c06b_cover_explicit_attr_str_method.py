from __future__ import annotations
import os


#@ ensures \result == 0
#@ assigns \nothing
def f(s: str, n: int) -> int:
    x = 0
    try:
        if n > 100:
            raise OSError("u")
        x = 1
        k = os.path.getsize(s)
    except OSError:
        return x
    return 0


if __name__ == "__main__":
    r = f("/no/such/rt58", 0)
    print("VIOLATION contract" if r != 0 else "result", r)
