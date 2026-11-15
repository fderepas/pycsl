from __future__ import annotations
import os


#@ requires n <= 100
#@ ensures \result == 0
#@ assigns \nothing
def f(s: str, n: int) -> int:
    try:
        if n > 100:
            raise OSError("u")
        k = os.path.getsize(s)
    except OSError:
        return 1
    return 0


if __name__ == "__main__":
    r = f("/no/such/u44", 0)
    print("VIOLATION contract" if r != 0 else "result", r)
