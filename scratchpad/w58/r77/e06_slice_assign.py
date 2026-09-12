from typing import List
#@ ensures \result == 1
def f() -> int:
    xs: List[int] = [1, 2, 3]
    xs[0:2] = [9]
    return xs[0]
if __name__ == "__main__":
    print(f())
