from typing import List, Tuple
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a: List[int] = []
    t: Tuple[List[int], int] = (a, 1)
    t[0].append(1)
    return len(a)

if __name__ == "__main__":
    print(f()); assert f() == 0
