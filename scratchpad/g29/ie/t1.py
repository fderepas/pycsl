r"""TypeError caught: int + str"""
from typing import List, Dict, Optional
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s = "a"
    try:
        v = len(s) + int(s == "a") * 0
        w = [1, 2][v:"x"]
    except TypeError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
