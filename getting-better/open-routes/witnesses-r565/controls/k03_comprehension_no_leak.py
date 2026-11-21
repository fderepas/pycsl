# u28 route #565 CONTROL: k03_comprehension_no_leak. The claim is TRUE of the program and must keep proving.
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    ys = [t for t in range(3)]
    if t is None:
        return 0
    return 1


if __name__ == "__main__":
    for a in (-1, 0, 1, 3):
        print(a, f(a))
