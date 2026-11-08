from dataclasses import dataclass
from typing import Dict, List, Set

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    xs: List[D] = [d]
    s = {xs[0]}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
