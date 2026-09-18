r"""set literal with duplicates len"""
from typing import Set, List, Dict, FrozenSet
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    s: Set[int] = {1, 1, 2}
    return len(s)


if __name__ == "__main__":
    print("CPython:", probe())
