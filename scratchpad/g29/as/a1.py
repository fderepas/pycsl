r"""assert statement failing caught"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    x = 1
    try:
        assert x == 2
    except AssertionError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
