r"""del list slice"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    xs: List[int] = [1, 2, 3]
    del xs[0:2]
    return len(xs)


if __name__ == "__main__":
    print("CPython:", probe())
