# u28 route #565 CONTROL: k14_optional_tuple. The claim is TRUE of the program and must keep proving.
from __future__ import annotations
from typing import Optional

#@ ensures x <= 0 ==> \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t: Optional[int] = None
    if x > 0:
        t, u = 1, 2
    if t is None:
        return 0
    return 1


if __name__ == "__main__":
    for a in (-1, 0, 1, 3):
        print(a, f(a))
