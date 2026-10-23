from typing import List
#@ ensures \result == 1
def f() -> int:
    a: List[int] = [1, 2, 3]
    return len(a[1:1])
if __name__ == "__main__":
    print(f())
