from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Any

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    xs = [d for _ in range(1)]
    s = {xs[0]}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
