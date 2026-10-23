r"""min with key"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = [1, -5, 3]
    return min(xs, key=abs)


if __name__ == "__main__":
    print("CPython:", probe())
