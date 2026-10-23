from typing import List
#@ ensures \result == 2
def f() -> int:
    a: List[int] = [1, 2]
    b: List[int] = a
    b.extend([3, 4])
    return len(a)
if __name__ == "__main__":
    print(f())
