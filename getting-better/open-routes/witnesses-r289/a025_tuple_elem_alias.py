from typing import List, Tuple

#@ ensures \result == 1
def f() -> int:
    a: List[int] = [1]
    t: Tuple[List[int], int] = (a, 0)
    b = t[0]
    b[0] = 5
    return a[0]

if __name__ == "__main__":
    assert f() == 1, f()
