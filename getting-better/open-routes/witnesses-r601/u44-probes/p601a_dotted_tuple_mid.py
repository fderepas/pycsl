from __future__ import annotations
import builtins


#@ ensures \result == 2
#@ assigns \nothing
def f(n: int) -> int:
    x = 0
    try:
        if n > 0:
            raise ValueError("v")
        x = 2
    except (builtins.ValueError, ZeroDivisionError):
        x = 7
    return x + 0 * n


if __name__ == "__main__":
    r = f(1)
    print("VIOLATION contract" if r != 2 else "result", r)
