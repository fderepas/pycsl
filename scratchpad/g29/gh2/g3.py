r"""old in an assert"""
from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe(a: List[int]) -> int:
    #@ assert \old(1) == 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
