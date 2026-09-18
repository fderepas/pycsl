r"""list multiplication negative"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    xs: List[int] = [1, 2] * -1
    return len(xs)


if __name__ == "__main__":
    print("CPython:", probe())
