r"""len of a non-ascii literal"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    return len("é")


if __name__ == "__main__":
    print("CPython:", probe())
