r"""unpack of a string"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    a, b = "abc"
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
