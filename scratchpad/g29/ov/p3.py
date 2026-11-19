r"""conditional expression evaluation order"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    x = 0
    y = 1 if x == 0 else 10 // x
    return y + 1


if __name__ == "__main__":
    print("CPython:", probe())
