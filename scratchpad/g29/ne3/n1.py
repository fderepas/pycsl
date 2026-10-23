r"""no_exception IndexError on list.pop from empty via helper"""
from typing import List, Dict
_ = 0  # anchor


#@ no_exception IndexError
#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1]
    i = 3
    v = xs[i - 1]
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
