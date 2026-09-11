from typing import List
#@ ensures \result == 1
def f() -> int:
    a: List[int] = [1]
    b: List[int] = a
    b.append(9)
    return a[1] if len(a) > 1 else 1
if __name__ == "__main__":
    print(f())
