# pycsl-flags: --memory-model hoare
from typing import Dict, List

#@ requires True
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f(a: int) -> int:
    return 1 // (a - a)
