r"""walrus in comprehension leaks to enclosing scope"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    y = 0
    xs = [(y := x) for x in [1, 2, 3]]
    return y


if __name__ == "__main__":
    print("CPython:", probe())
