r"""slice beyond end is clipped"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    xs: List[int] = [1, 2]
    return len(xs[0:5])


if __name__ == "__main__":
    print("CPython:", probe())
