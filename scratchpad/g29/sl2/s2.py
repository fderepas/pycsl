r"""negative slice bounds"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    xs: List[int] = [1, 2, 3]
    return len(xs[-1:])


if __name__ == "__main__":
    print("CPython:", probe())
