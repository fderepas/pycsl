from typing import List
#@ requires x == 1
def g(x: int) -> int:
    return x

#@ ensures \result == 1
def f() -> int:
    xs: List[int] = [1, 2, 3]
    del xs[0:2]
    return g(xs[0])
if __name__ == "__main__":
    print(f())
