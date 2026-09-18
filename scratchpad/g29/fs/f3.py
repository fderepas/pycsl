r"""format percent"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    return len("%d%%" % 5)


if __name__ == "__main__":
    print("CPython:", probe())
