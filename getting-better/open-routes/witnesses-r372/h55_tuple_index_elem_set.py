from dataclasses import dataclass
from typing import Tuple

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(t: Tuple[D, int]) -> int:
    s = {t[0]}
    return 1

if __name__ == "__main__":
    print(g((D(1), 2)))
