r"""augmented list extend"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = [1]
    xs += [2, 3]
    return len(xs)


if __name__ == "__main__":
    print("CPython:", probe())
