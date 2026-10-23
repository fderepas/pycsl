r"""map with lambda dividing"""
from typing import Dict, List
_ = 0  # anchor


#@ no_exception ZeroDivisionError
#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [0]
    ys = list(map(lambda x: 10 // x, xs))
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
