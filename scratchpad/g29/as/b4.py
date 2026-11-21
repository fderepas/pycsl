r"""assert in for"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    for i in range(2):
        assert i == 7
    return 5


if __name__ == "__main__":
    print("CPython:", probe())
