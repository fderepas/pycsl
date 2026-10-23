r"""string to int of float text caught"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    try:
        v = int("1.5")
    except ValueError:
        return 9
    return v * 0


if __name__ == "__main__":
    print("CPython:", probe())
