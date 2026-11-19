r"""OverflowError caught from float conversion"""
from typing import List, Dict, Optional
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    try:
        f = float(10 ** 400)
    except ArithmeticError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
