from typing import List
#@ requires len(xs) == 2 and xs[0] == 1
#@ ensures \result == 1
def f(xs: List[int]) -> int:
    for k in range(1):
        xs = [7, 7]
    return xs[0]

if __name__ == "__main__":
    assert f([1, 2]) == 1, f([1, 2])
