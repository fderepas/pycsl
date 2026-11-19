r"""reverse slice"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = [1, 2, 3]
    return xs[::-1][0]


if __name__ == "__main__":
    print("CPython:", probe())
