r"""enumerate start"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [7]
    r = -1
    for i, v in enumerate(xs, start=5):
        r = i
    return r


if __name__ == "__main__":
    print("CPython:", probe())
