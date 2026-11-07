r"""ord of a non-ascii literal bound to a local"""
from typing import List
_ = 0  # anchor


#@ ensures \result < 256
def probe() -> int:
    s = "é"
    return ord(s)


if __name__ == "__main__":
    print("CPython:", probe())
