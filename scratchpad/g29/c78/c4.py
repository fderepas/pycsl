r"""set comprehension division"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ no_exception ZeroDivisionError
#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [0]
    s = {10 // x for x in xs}
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
