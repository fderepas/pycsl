from dataclasses import dataclass
from typing import Optional


@dataclass
class D:
    s: Optional[str] = "abc"


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    d = D()
    if d.s is None:
        return 1
    return 0
