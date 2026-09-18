r"""dict keys equal after update order"""
from typing import Set, List, Dict, FrozenSet
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    d: Dict[int, int] = {1: 1, 2: 2}
    d[1] = 5
    return len(d) + 0


if __name__ == "__main__":
    print("CPython:", probe())
