r"""optional zero is falsy but not None"""
from typing import List, Optional, Union
_ = 0  # anchor


def f(x: Optional[int]) -> int:
    if x:
        return 1
    if x is None:
        return 2
    return 3


#@ ensures \result == 2
def probe() -> int:
    return f(0)


if __name__ == "__main__":
    print("CPython:", probe())
