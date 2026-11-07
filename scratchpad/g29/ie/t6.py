r"""UnicodeDecodeError caught"""
from typing import List, Dict, Optional
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    b = bytes([255])
    try:
        s = b.decode("utf-8")
    except UnicodeDecodeError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
