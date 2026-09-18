r"""f-string length with format spec"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    return len(f"{5:03d}")


if __name__ == "__main__":
    print("CPython:", probe())
