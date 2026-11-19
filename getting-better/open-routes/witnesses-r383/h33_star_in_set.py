from dataclasses import dataclass
from typing import List

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(ds: List[D]) -> int:
    s = {*ds}
    return 1

if __name__ == "__main__":
    print(g([D(1)]))
