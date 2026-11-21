from typing import List
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: List[int] = [0]
    b: List[int] = a
    b += [1]
    return len(a)

if __name__ == "__main__":
    print(f()); assert f() == 1
