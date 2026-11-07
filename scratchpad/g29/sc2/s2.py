r"""for loop variable leaks"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 7
def probe() -> int:
    x = 7
    for x in [1, 2]:
        pass
    return x


if __name__ == "__main__":
    print("CPython:", probe())
