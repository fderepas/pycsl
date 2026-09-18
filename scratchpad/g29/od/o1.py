r"""old of param list after store through same list passed twice"""
from typing import List
_ = 0  # anchor


#@ requires len(a) >= 1 and len(b) >= 1
#@ assigns a[0]
#@ ensures b[0] == \old(b[0])
def f(a: List[int], b: List[int]) -> None:
    a[0] = 5


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [0]
    f(xs, xs)
    return xs[0]


if __name__ == "__main__":
    print("CPython:", probe())
