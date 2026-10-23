r"""struct.unpack first element"""
import struct
from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    t = struct.unpack(">H", b"\x01\x02")
    return t[0]


if __name__ == "__main__":
    print("CPython:", probe())
