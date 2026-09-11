# pycsl-flags: --memory-model hoare
from typing import Set

_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    s: Set[int] = {1}
    s.remove(5)
    return 0
