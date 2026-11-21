from dataclasses import dataclass
from typing import Dict

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 0
def f(kw: Dict[str, int]) -> int:
    d = D(**kw)
    return d.x

if __name__ == "__main__":
    print(f({"x": 3}))
