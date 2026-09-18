r"""non-empty list truthiness after pop-free append"""
from typing import List, Dict, Set
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = []
    xs.append(1)
    if xs:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
