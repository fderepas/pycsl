r"""float division by zero caught"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    z = 0.0
    try:
        v = 1.0 / z
    except ZeroDivisionError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
