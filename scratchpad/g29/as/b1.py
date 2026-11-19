r"""top-level false assert"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    x = 3
    assert x < 2
    return 5


if __name__ == "__main__":
    print("CPython:", probe())
