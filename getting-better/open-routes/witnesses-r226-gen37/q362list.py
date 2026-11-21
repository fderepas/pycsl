from dataclasses import dataclass, field
from typing import List

#@ class invariant self.x >= 0
@dataclass
class D:
    x: int
    xs: List[int] = field(default_factory=list)

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    assert f(D(-1)) >= 0
