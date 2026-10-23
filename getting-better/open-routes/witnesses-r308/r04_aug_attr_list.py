from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == 2
def f() -> int:
    c = [0]
    ys = [0, 0, 0]
    ys[inc(c) - 1] -= 1
    return c[0]

if __name__ == "__main__":
    assert f() == 2
