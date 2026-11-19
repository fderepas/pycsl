r"""no_exception IndexError over comprehension indexing out of range"""
from typing import Dict, List
_ = 0  # anchor


#@ no_exception IndexError
#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1]
    ys = [xs[i] for i in range(3)]
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
