# u28 route #565 family probe: q18_global. CPython f(1) != 0, so `ensures \result == 0` is FALSE.
from __future__ import annotations
GT = None


def h() -> None:
    global GT
    GT = 1

#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    global GT
    GT = None
    h()
    if GT is None:
        return 0
    return 1


if __name__ == "__main__":
    print("VIOLATION" if f(1) != 0 else "ok", f(1))
