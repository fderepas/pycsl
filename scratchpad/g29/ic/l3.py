r"""for-loop invariant false after body"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s = 0
    #@ loop invariant s == 0
    for i in range(3):
        s = s + i
    return s


if __name__ == "__main__":
    print("CPython:", probe())
