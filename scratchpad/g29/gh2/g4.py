r"""ghost array copy range"""
from typing import List
_ = 0  # anchor


#@ requires len(a) >= 2
#@ ensures \result == 0
def probe(a: List[int]) -> int:
    #@ ghost int[] snap = \copy_range(a, 0, 2)
    a[0] = 5
    #@ assert snap[0] == 5
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
