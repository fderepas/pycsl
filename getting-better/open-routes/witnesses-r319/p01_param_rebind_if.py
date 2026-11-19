from typing import List
#@ requires len(xs) == 2
#@ ensures \result == 2
def f(xs: List[int], b: bool) -> int:
    if b:
        xs = [7, 7, 7]
    return len(xs)

if __name__ == "__main__":
    assert f([1, 2], True) == 2, f([1, 2], True)
