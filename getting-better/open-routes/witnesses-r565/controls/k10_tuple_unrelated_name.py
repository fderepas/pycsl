# u28 route #565 CONTROL: k10_tuple_unrelated_name. The claim is TRUE of the program and must keep proving.
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    a, b = x, 2
    if t is None:
        return 0
    return 1


if __name__ == "__main__":
    for a in (-1, 0, 1, 3):
        print(a, f(a))
