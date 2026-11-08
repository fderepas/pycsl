r"""match capture binds name"""
from typing import List, Tuple
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    x = 7
    match x:
        case y:
            return y


if __name__ == "__main__":
    print("CPython:", probe())
