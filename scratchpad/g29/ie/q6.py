r"""all() generator with division"""
from typing import Dict, List
_ = 0  # anchor


#@ no_exception ZeroDivisionError
#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [0]
    b = all(10 // x > 0 for x in xs)
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
