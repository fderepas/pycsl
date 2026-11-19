r"""abs of bool and int comparisons"""
import math
from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    return abs(-True)


if __name__ == "__main__":
    print("CPython:", probe())
