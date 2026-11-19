from typing import List
#@ ensures \result == 1
def f(n: int) -> int:
    xs: List[int] = [1, 2, 3]
    del xs[0:n]
    return xs[0]
if __name__ == "__main__":
    print(f(2))
