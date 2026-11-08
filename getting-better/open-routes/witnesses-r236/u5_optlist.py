from dataclasses import dataclass
from typing import List, Optional


@dataclass
class P:
    x: int
    items: Optional[List[int]] = None


#@ ensures \result.items == 0
#@ assigns \nothing
def f(c: int) -> P:
    return P(c)
