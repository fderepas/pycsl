from typing import List
#@ ensures \result == 2
def f() -> int:
    a: List[int] = [1, 2]
    b: List[int] = a
    a.append(3)
    return len(b)
if __name__ == "__main__":
    print(f())
