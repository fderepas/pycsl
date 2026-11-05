# u28 route #565 CONTROL: k07_none_falsy. The claim is TRUE of the program and must keep proving.
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    if t:
        return 7
    return 0


if __name__ == "__main__":
    for a in (-1, 0, 1, 3):
        print(a, f(a))
