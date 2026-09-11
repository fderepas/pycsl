# pycsl-flags: --memory-model hoare
from typing import Dict

_ = 0
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    d: Dict[str, int] = {"a": 1, "b": 2}
    return len(d)
