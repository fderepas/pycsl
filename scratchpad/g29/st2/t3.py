r"""set from list len"""
from typing import Set, List, Dict, FrozenSet
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    xs: List[int] = [1, 1, 2]
    return len(set(xs))


if __name__ == "__main__":
    print("CPython:", probe())
