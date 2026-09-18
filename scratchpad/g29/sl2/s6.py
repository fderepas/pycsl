r"""string slice out of range is empty"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    s = "ab"
    return len(s[5:7])


if __name__ == "__main__":
    print("CPython:", probe())
