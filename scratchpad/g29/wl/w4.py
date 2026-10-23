r"""walrus in any() leaks witness"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    w = 0
    if any((w := x) > 1 for x in [1, 2, 3]):
        return w
    return -1


if __name__ == "__main__":
    print("CPython:", probe())
