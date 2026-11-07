from typing import List
from rt8h2 import ident2

#@ requires \length(a) == 1
#@ ensures \result == \old(a[0])
def f(a: List[int]) -> int:
    b = ident2(a)
    b[0] = a[0] + 1
    return a[0]

if __name__ == "__main__":
    assert f([1]) == 1, f([1])
