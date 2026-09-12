from typing import List
#@ ensures \result == 3
def f() -> int:
    xs: List[int] = [1, 2, 3]
    del xs[-1]
    return xs[-1]
if __name__ == "__main__":
    print(f())
