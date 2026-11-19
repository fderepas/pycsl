from typing import List

#@ requires True
#@ ensures \result == 0
#@ assigns xs
def sneak(xs: List[int]) -> int:
    xs[0] = 99
    return 0

#@ ensures \result == 1
def f() -> int:
    xs: List[int] = [1, 2, 3]
    assert sneak(xs) == 0
    return xs[0]
if __name__ == "__main__":
    print(f())
