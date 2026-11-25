from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class R:
    x: float
    f: List[Tuple[str, bool, List[str]]] = field(default_factory=list)


#@ requires True
#@ ensures True
def g(r: R) -> Dict[str, PyVal]:
    return {"x": r.x, "f": [[b, a] for (a, b, c) in r.f], "g": [c for (a, b, c) in r.f]}


#@ requires True
#@ ensures \result == 1
def h(r: R) -> int:
    d = g(r)
    v = d["x"]
    if isinstance(v, float):
        return 1
    return 0
