from dataclasses import dataclass
from typing import ClassVar as CV

@dataclass
class D:
    x: int
    k: CV[int] = 3

#@ no_exception \all
def f() -> int:
    d = D(1, 5)
    return d.x

if __name__ == "__main__":
    print(f())
