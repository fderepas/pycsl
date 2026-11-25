from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class R:
    d: Dict[int, List[int]] = field(default_factory=dict)
    f: List[Tuple[str, bool, List[str]]] = field(default_factory=list)


#@ requires True
#@ ensures \result == 0
def g(r: R) -> int:
    n = 0
    for (a, b, c) in r.f:
        n = n + len(c)
    return n
