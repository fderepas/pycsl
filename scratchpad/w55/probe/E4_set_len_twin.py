# pycsl-flags: --memory-model hoare
from typing import Set

_ = 0
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    s: Set[int] = {1}
    s.add(1)
    return len(s)
