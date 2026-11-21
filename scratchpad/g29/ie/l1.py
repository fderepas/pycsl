r"""no_exception ZeroDivisionError over comprehension dividing by zero"""
from typing import Dict, List
_ = 0  # anchor


#@ no_exception ZeroDivisionError
#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [0, 1]
    ys = [10 // x for x in xs]
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
