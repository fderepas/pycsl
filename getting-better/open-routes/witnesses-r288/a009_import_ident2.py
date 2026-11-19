from typing import List
from rt8helper import ident2

#@ ensures \result == 1
def f() -> int:
    a: List[int] = [1]
    b: List[int] = ident2(a)
    b[0] = 5
    return a[0]

if __name__ == "__main__":
    assert f() == 1, f()
