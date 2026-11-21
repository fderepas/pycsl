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
    for i in range(inc(c), inc(c) + 5):
        return i
    return -1

if __name__ == "__main__":
    assert f() == 2
