# pycsl-flags: --memory-model hoare
from typing import Dict, List

#@ requires True
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f(i: int) -> int:
    xs: List[int] = [1]
    return xs[i]
