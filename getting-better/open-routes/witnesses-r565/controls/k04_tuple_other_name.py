# u28 route #565 CONTROL: k04_tuple_other_name. The claim is TRUE of the program and must keep proving.
from __future__ import annotations


#@ ensures \result == 2
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    t, u = x, 2
    return u


if __name__ == "__main__":
    for a in (-1, 0, 1, 3):
        print(a, f(a))
