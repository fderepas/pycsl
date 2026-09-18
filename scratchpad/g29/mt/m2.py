r"""match or-pattern"""
from typing import List, Tuple
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    x = 3
    match x:
        case 1 | 3:
            return 1
        case _:
            return 2


if __name__ == "__main__":
    print("CPython:", probe())
