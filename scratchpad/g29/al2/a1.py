r"""G29 AL2-A1 — the SAME list passed for two list parameters (aliased arguments)."""
from typing import List
_ = 0  # anchor


#@ requires len(a) >= 1 and len(b) >= 1
#@ ensures a[0] == \old(a[0]) + 1
#@ ensures b[0] == \old(b[0])
#@ assigns a[0]
def f(a: List[int], b: List[int]) -> None:
    a[0] = a[0] + 1


#@ ensures \result == 5
def probe() -> int:
    xs: List[int] = [5]
    f(xs, xs)
    return xs[0]


if __name__ == "__main__":
    print("CPython:", probe())
