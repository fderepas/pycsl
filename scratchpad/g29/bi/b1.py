r"""sorted first element"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    xs: List[int] = [3, 1, 2]
    return sorted(xs)[0]


if __name__ == "__main__":
    print("CPython:", probe())
