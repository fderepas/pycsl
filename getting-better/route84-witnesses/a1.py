from typing import List

#@ ensures \result == 3
def f() -> int:
    xs: List[int] = [1, 2, 3]
    assert xs.pop() == 3
    return len(xs)
if __name__ == "__main__":
    print(f())
