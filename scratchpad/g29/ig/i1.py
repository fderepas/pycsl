r"""iterate dict keys while inserting"""
from typing import List, Dict, Iterator
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    d: Dict[int, int] = {0: 0}
    n = 0
    for k in list(d):
        d[k + 1] = 1
        n = n + 1
    return n + 1


if __name__ == "__main__":
    print("CPython:", probe())
