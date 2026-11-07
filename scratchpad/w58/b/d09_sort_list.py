from typing import List
#@ ensures \result == 3
def f() -> int:
    xs: List[int] = [3, 1, 2]
    xs.sort()
    return xs[0]
if __name__ == "__main__":
    print(f())
