r"""augmented assign on list element in loop"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [0, 0]
    for i in range(2):
        xs[i] += 1
    return xs[0] + xs[1]


if __name__ == "__main__":
    print("CPython:", probe())
