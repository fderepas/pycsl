from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ assigns d[1]
#@ requires 1 in d
#@ ensures d[1] == 9 and \result == 0
def setd(d: Dict[int, int]) -> int:
    d[1] = 9
    return 0

#@ ensures \result == 9
def f() -> int:
    d: Dict[int, int] = {1: 0}
    return d[1] + setd(d)

if __name__ == "__main__":
    assert f() == 9
