from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

class K:
    def __init__(self, a: List[int]) -> None:
        self.ys = a[0:inc(a)]

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    k = K(xs)
    return xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
