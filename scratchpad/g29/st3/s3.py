r"""struct.calcsize"""
import struct
from typing import List
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    return struct.calcsize(">HB")


if __name__ == "__main__":
    print("CPython:", probe())
