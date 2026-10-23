r"""list.sort mutates in place"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    xs: List[int] = [3, 1, 2]
    xs.sort()
    return xs[0]


if __name__ == "__main__":
    print("CPython:", probe())
