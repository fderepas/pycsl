# pycsl-flags: --memory-model hoare
from typing import List

#@ requires True
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f(a: int) -> int:
    xs: List[int] = [1]
    with open("x"):
        b = xs[5]
    return 0
