r"""no_exception IndexError string negative"""
from typing import List, Dict
_ = 0  # anchor


#@ no_exception IndexError
#@ ensures \result == 0
def probe() -> int:
    s = "ab"
    c = s[-3]
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
