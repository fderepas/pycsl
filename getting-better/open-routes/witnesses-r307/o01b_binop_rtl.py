from typing import List

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == 10 and \result == \old(a[0])
def setten(a: List[int]) -> int:
    old = a[0]
    a[0] = 10
    return old

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == 20 and \result == \old(a[0])
def settwenty(a: List[int]) -> int:
    old = a[0]
    a[0] = 20
    return old

#@ ensures \result == 20
def f() -> int:
    xs = [0]
    r = setten(xs) + settwenty(xs)
    return r

if __name__ == "__main__":
    assert f() == 20
