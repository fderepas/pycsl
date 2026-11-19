r"""set intersection empty truthiness"""
from typing import Set, List, Dict, FrozenSet
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    a: Set[int] = {1}
    b: Set[int] = {2}
    if a & b:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
