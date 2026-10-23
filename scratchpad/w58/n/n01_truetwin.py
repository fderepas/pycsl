from typing import List
#@ ensures \result == 3
def f() -> int:
    a: List[int] = [1, 2]
    b: List[int] = a
    b.append(3)
    return len(a)
if __name__ == "__main__":
    print(f())
