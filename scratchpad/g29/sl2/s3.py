r"""slice with step"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    xs: List[int] = [1, 2, 3, 4]
    return len(xs[::2])


if __name__ == "__main__":
    print("CPython:", probe())
