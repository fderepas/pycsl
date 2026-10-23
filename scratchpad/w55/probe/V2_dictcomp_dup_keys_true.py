# pycsl-flags: --memory-model hoare
from typing import Dict, List

_ = 0
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: List[int] = [1, 1]
    d: Dict[int, int] = {x: x for x in a}
    return len(d)
