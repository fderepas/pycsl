from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class R:
    f: List[Tuple[str, bool, List[str]]] = field(default_factory=list)


#@ requires True
#@ ensures \result == 0
def g(r: R) -> int:
    n = 0
    for (a, b, c) in r.f:
        n = n + len(c)
    return n
