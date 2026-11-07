r"""comprehension variable does not leak"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    x = 7
    ys = [x for x in [1, 2]]
    return x


if __name__ == "__main__":
    print("CPython:", probe())
