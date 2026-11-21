from lib5 import idx
from typing import List
_ = 0  # anchor


#@ no_exception IndexError
#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1]
    return idx(xs) * 0


if __name__ == "__main__":
    print("CPython:", probe())
