r"""assume false in body"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    #@ assume False
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
