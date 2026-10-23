# pycsl-flags: --memory-model hoare
from typing import Dict

_ = 0
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d: Dict[str, int] = {"ab": 1}
    k = "a" + "b"
    return d[k]
