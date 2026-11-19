r"""list.count and in"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = [1, 1, 2]
    return xs.count(1) + (1 if 3 in xs else 0)


if __name__ == "__main__":
    print("CPython:", probe())
