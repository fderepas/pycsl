r"""assert in else"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    x = 3
    if x < 2:
        pass
    else:
        assert x < 2
    return 5


if __name__ == "__main__":
    print("CPython:", probe())
