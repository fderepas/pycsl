r"""no_exception IndexError in caller; helper reads out of range"""
from typing import List
_ = 0  # anchor


def get(xs: List[int]) -> int:
    return xs[5]


#@ no_exception IndexError
#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1]
    v = get(xs)
    return v * 0


if __name__ == "__main__":
    print("CPython:", probe())
