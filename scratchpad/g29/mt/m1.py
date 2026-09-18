r"""match guard false falls through"""
from typing import List, Tuple
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    x = 5
    match x:
        case 5 if x > 10:
            return 1
        case _:
            return 2


if __name__ == "__main__":
    print("CPython:", probe())
