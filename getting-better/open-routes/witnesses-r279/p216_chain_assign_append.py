from typing import List
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a: List[int] = []
    b: List[int] = []
    a = b = []
    b.append(1)
    return len(a)

if __name__ == "__main__":
    print(f()); assert f() == 0
