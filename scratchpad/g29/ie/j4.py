r"""missing int key caught"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[int, int] = {1: 1}
    try:
        v = d[2]
    except KeyError:
        return 9
    return v

if __name__ == "__main__":
    print("CPython:", probe())
