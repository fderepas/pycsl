from typing import List

#@ requires n == 3
#@ ensures \result == n
def g(n: int) -> int:
    return n

#@ ensures \result == 3
def f() -> int:
    xs: List[int] = [1, 2, 3]
    assert xs.pop() == 3
    return g(len(xs))
if __name__ == "__main__":
    print(f())
