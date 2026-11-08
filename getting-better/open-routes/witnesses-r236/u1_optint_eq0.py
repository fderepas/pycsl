from dataclasses import dataclass
from typing import Optional


@dataclass
class P:
    x: int
    k: Optional[int] = None


#@ ensures \result.k == 0
#@ assigns \nothing
def f(c: int) -> P:
    return P(c)
