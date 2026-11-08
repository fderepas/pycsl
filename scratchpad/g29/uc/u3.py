r"""slicing a multi-byte string"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    s = "éa"
    return len(s[0:1])


if __name__ == "__main__":
    print("CPython:", probe())
