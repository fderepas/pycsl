import itertools
from typing import List
#@ requires len(xs) == 2
#@ ensures \result == 2
#@ assigns \nothing
def f(xs: List[int]) -> int:
    return len(list(itertools.product(xs, repeat=2)))

if __name__ == "__main__":
    assert f([1, 2]) == 2, f([1, 2])
