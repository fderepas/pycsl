r"""encode length of a non-ascii string"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    s = "é"
    return len(s.encode("utf-8"))


if __name__ == "__main__":
    print("CPython:", probe())
