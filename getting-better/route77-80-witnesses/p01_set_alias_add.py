from typing import Set
#@ ensures \result == 1
def f() -> int:
    a: Set[int] = {1}
    b: Set[int] = a
    b.add(2)
    return len(a)
if __name__ == "__main__":
    print(f())
