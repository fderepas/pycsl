r"""missing key in ternary caught"""
from typing import Dict, List, Set
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[int, int] = {1: 1}
    try:
        v = d[2] if True else 0
    except KeyError:
        return 9
    return v * 0


if __name__ == "__main__":
    print("CPython:", probe())
