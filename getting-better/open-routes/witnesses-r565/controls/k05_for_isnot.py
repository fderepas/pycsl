# u28 route #565 CONTROL: k05_for_isnot. The claim is TRUE of the program and must keep proving.
from __future__ import annotations


#@ ensures \result == 1
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    for t in [x]:
        pass
    if t is not None:
        return 1
    return 1


if __name__ == "__main__":
    for a in (-1, 0, 1, 3):
        print(a, f(a))
