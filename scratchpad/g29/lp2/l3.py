r"""loop var value after loop"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    i = -1
    for i in range(5):
        pass
    return i


if __name__ == "__main__":
    print("CPython:", probe())
