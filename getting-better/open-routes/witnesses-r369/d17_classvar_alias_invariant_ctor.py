from dataclasses import dataclass
from typing import ClassVar as CV

@dataclass
class D:
    x: int
    k: CV[int] = -1

#@ ensures \result == 5
def f() -> int:
    d = D(1, 5)
    return 5

if __name__ == "__main__":
    print(f())
