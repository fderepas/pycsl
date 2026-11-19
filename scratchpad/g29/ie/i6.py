r"""exception from called function caught"""
from typing import List, Dict
_ = 0  # anchor


def boom(z: int) -> int:
    return 10 // z


#@ ensures \result == 0
def probe() -> int:
    try:
        v = boom(0)
    except ZeroDivisionError:
        return 9
    return v

if __name__ == "__main__":
    print("CPython:", probe())
