from typing import List

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == 2
def f() -> int:
    xs = [0]
    d = {1: 0, 2: 0, 3: 0}
    d[inc(xs)] += 1
    return xs[0]

if __name__ == "__main__":
    assert f() == 2
