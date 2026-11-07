r"""imported empty list index caught"""
from typing import List
from lib6 import parse, pair, shift, first
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = []
    try:
        v = first(xs)
    except IndexError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
