from dataclasses import dataclass
from typing import Optional


@dataclass
class P:
    x: int
    name: Optional[str] = None


#@ ensures \result.name == 0
#@ assigns \nothing
def f(c: int) -> P:
    return P(c)
