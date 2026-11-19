r"""no_exception IndexError negative index too small"""
from typing import List, Dict
_ = 0  # anchor


#@ no_exception IndexError
#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1, 2]
    v = xs[-3]
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
