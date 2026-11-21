r"""walrus in generator passed to sum"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    last = 0
    t = sum((last := x) for x in [1, 2, 3])
    return last


if __name__ == "__main__":
    print("CPython:", probe())
