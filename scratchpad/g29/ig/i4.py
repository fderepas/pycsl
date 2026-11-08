r"""iterate dict items sum"""
from typing import List, Dict, Iterator
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[int, int] = {1: 2, 3: 4}
    s = 0
    for k, v in d.items():
        s = s + v
    return s


if __name__ == "__main__":
    print("CPython:", probe())
