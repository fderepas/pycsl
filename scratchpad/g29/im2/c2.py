r"""imported list length"""
from typing import List
_ = 0  # anchor


from libc import NAMES


#@ ensures \result == 0
def probe() -> int:
    return len(NAMES)


if __name__ == "__main__":
    print("CPython:", probe())
