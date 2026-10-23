# pycsl-flags: --memory-model hoare
from typing import Dict, Optional

_ = 0
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    d: Dict[int, Optional[int]] = {1: None}
    return len(d)
