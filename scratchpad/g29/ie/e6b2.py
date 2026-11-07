r"""pop from empty list caught"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = []
    try:
        v = xs[0]
    except:
        return 9
    return v * 0


if __name__ == "__main__":
    print("CPython:", probe())
