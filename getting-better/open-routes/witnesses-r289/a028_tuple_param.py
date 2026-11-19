from typing import List, Tuple

#@ requires \length(xs) == 1
#@ ensures \result == \old(xs[0])
def f(xs: List[int]) -> int:
    t: Tuple[List[int], int] = (xs, 0)
    b = t[0]
    b[0] = 5
    return xs[0]

if __name__ == "__main__":
    assert f([1]) == 1, f([1])
