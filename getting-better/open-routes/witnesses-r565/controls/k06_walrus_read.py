# u28 route #565 CONTROL: k06_walrus_read. The claim is TRUE of the program and must keep proving.
from __future__ import annotations


#@ ensures \result >= 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    if (t := x) > 0:
        return t
    return 0


if __name__ == "__main__":
    for a in (-1, 0, 1, 3):
        print(a, f(a))
