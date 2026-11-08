r"""imported constant value"""
from typing import List
_ = 0  # anchor


from libc import LIMIT


#@ ensures \result == 0
def probe() -> int:
    return LIMIT


if __name__ == "__main__":
    print("CPython:", probe())
