from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == 2
def f() -> int:
    xs = [0]
    xs[0] += inc(xs)
    return xs[0]

if __name__ == "__main__":
    assert f() == 2
