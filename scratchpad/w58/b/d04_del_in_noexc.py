from typing import List
#@ ensures \result == 1
#@ no_exception IndexError
def f() -> int:
    xs: List[int] = [1, 2, 3]
    del xs[0]
    return xs[0]
if __name__ == "__main__":
    print(f())
