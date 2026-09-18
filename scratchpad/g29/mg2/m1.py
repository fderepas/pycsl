r"""module global list mutated at import time"""
from typing import List, Dict
_ = 0  # anchor


xs: List[int] = [1]
xs.append(2)


#@ ensures \result == 1
def probe() -> int:
    return len(xs)


if __name__ == "__main__":
    print("CPython:", probe())
