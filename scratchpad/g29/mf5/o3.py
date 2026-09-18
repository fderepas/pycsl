r"""imported negative shift under no_exception"""
from typing import List
from lib6 import parse, pair, shift, first
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    v = shift(-1)
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
