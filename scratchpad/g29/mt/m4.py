r"""match no case matches returns None path"""
from typing import List, Tuple
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    x = 7
    r = 0
    match x:
        case 1:
            r = 1
    return r + 0


if __name__ == "__main__":
    print("CPython:", probe())
