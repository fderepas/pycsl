# pycsl-flags: --memory-model hoare
from typing import List, Set

_ = 0
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    a: List[int] = [1, 1]
    s: Set[int] = {x for x in a}
    return len(s)
