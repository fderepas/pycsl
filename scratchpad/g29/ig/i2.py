r"""iterate over set"""
from typing import List, Dict, Iterator
_ = 0  # anchor


from typing import Set


#@ ensures \result == 0
def probe() -> int:
    s: Set[int] = {1, 2}
    n = 0
    for x in s:
        n = n + x
    return n


if __name__ == "__main__":
    print("CPython:", probe())
