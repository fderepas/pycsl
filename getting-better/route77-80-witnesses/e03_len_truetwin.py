from typing import List
#@ ensures \result == 1
def f() -> int:
    xs: List[int] = [1, 2, 3]
    del xs[0:2]
    return len(xs)
if __name__ == "__main__":
    print(f())
