r"""struct.pack length"""
import struct
from typing import List
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    b = struct.pack(">H", 258)
    return len(b)


if __name__ == "__main__":
    print("CPython:", probe())
