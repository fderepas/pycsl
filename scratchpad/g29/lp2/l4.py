r"""loop var after empty range"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    i = 7
    for i in range(0):
        pass
    return i


if __name__ == "__main__":
    print("CPython:", probe())
