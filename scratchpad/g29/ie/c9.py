r"""dict value read in a while loop with try around the loop"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[int, int] = {0: 0}
    i = 0
    s = 0
    try:
        while i < 2:
            s = s + d[i]
            i = i + 1
    except KeyError:
        return 9
    return s


if __name__ == "__main__":
    print("CPython:", probe())
