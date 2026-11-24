from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

PyVal = Any


@dataclass
class R:
    d: Dict[int, List[int]] = field(default_factory=dict)
    f: List[Tuple[str, List[str]]] = field(default_factory=list)

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def g(r: R) -> int:
    t = r.f[0]
    return len(t[1])


if __name__ == "__main__":
    print("CPython g(R({}, [('a', ['z'])])) =", g(R({}, [("a", ["z"])])))
