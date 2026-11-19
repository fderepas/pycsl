# u28 route #565 CONTROL: k02_isnot_narrow_tuple. The claim is TRUE of the program and must keep proving.
from __future__ import annotations


#@ ensures \result >= 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    u = None
    if x > 0:
        t, u = 1, 2
    if t is not None:
        return t
    return 0


if __name__ == "__main__":
    for a in (-1, 0, 1, 3):
        print(a, f(a))
