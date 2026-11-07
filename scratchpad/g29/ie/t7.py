r"""ValueError from str.split unpack caught"""
from typing import List, Dict, Optional
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s = "a"
    try:
        a, b = s.split(",")
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
