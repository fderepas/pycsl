r"""set difference membership"""
from typing import Set, List, Dict, FrozenSet
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    a: Set[int] = {1, 2}
    b: Set[int] = {1}
    return 1 in (a - b)


if __name__ == "__main__":
    print("CPython:", probe())
