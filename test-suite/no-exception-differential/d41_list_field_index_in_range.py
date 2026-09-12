# pycsl-flags: --memory-model hoare
"""d41 RETURNS — the in-range twin of d40. Index 1 of `[1, 2, 3]` is 2 and nothing raises, so
this is the direction that keeps the gate from being satisfiable by refusing everything."""
from typing import List


class C:
    xs: List[int]

    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs = [1, 2, 3]


#@ requires True
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.xs[1]


if __name__ == "__main__":
    f()
