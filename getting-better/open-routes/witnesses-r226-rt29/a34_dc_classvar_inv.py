from dataclasses import dataclass
from typing import ClassVar

#@ class invariant self.k >= 0
@dataclass
class D:
    x: int
    k: ClassVar[int] = -1

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.k

if __name__ == "__main__":
    print(f(D(1)))
