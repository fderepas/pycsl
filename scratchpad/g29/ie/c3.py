r"""max of empty caught"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = []
    try:
        v = max(xs)
    except ValueError:
        return 9
    return v


if __name__ == "__main__":
    print("CPython:", probe())
