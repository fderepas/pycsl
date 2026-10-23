r"""sum with start"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ ensures \result == 6
def probe() -> int:
    xs: List[int] = [1, 2, 3]
    return sum(xs, 10)


if __name__ == "__main__":
    print("CPython:", probe())
