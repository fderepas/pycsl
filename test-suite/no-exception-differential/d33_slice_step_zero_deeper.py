# pycsl-flags: --memory-model hoare
from typing import List

#@ ensures True
#@ assigns \nothing
def g(xs: List[int]) -> int:
    ys = xs[::0]
    return len(ys)

_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2]
    return g(xs)

if __name__ == "__main__":
    f()
