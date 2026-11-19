r"""tuple swap"""
from typing import List, Tuple, Dict
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    a = 1
    b = 2
    a, b = b, a
    return a


if __name__ == "__main__":
    print("CPython:", probe())
