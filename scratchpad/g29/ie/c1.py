r"""list.index missing caught"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1, 2]
    try:
        v = xs.index(7)
    except ValueError:
        return 9
    return v


if __name__ == "__main__":
    print("CPython:", probe())
