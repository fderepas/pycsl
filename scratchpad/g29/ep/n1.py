r"""no_exception all with a handled construct"""
from typing import List, Dict
_ = 0  # anchor


#@ no_exception \all
#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1]
    return xs[0] * 0


if __name__ == "__main__":
    print("CPython:", probe())
