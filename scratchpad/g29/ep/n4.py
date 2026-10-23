r"""no_exception StopIteration on a for loop"""
from typing import List, Dict
_ = 0  # anchor


#@ no_exception StopIteration
#@ ensures \result == 0
def probe() -> int:
    n = 0
    for x in [1, 2]:
        n = n + 1
    return n - 2


if __name__ == "__main__":
    print("CPython:", probe())
