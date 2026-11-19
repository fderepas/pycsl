"""v46 AGREE — ROUTE #87's completeness gain. The list literal now reaches the allocation site
as the `let _alit = Array.make n (v0) in _alit[i] <- vi; ... _alit` chain a LOCAL list literal
always got, so the TRUE element value is provable. CPython returns 2."""
from typing import List


class C:
    xs: List[int]

    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs = [1, 2, 3]


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.xs[1]


if __name__ == "__main__":
    print(f())
