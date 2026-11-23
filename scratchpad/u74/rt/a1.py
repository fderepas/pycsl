from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class R:
    f: List[Tuple[str, bool, List[str]]] = field(default_factory=list)


#@ requires True
#@ ensures \result == 0
def g() -> int:
    r = R()
    xs: List[str] = []
    r.f.append(("a", True, xs))
    xs.append("z")
    t = r.f[0]
    return len(t[2])


if __name__ == "__main__":
    print("CPython g() =", g())
