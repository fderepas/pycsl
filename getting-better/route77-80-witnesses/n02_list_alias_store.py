from typing import List
#@ ensures \result == 1
def f() -> int:
    a: List[int] = [1, 2]
    b: List[int] = a
    b[0] = 9
    return a[0]
if __name__ == "__main__":
    print(f())
