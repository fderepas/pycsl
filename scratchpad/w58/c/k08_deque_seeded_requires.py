from collections import deque
#@ requires x == 0
def g(x: int) -> int:
    return x

#@ ensures \result == 0
def f() -> int:
    dq = deque([1, 2, 3])
    return g(len(dq))
if __name__ == "__main__":
    print(f())
