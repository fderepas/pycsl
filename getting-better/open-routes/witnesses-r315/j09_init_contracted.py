from typing import List

class K:
    #@ requires len(a) >= 1
    #@ assigns a[0]
    #@ ensures a[0] == \old(a[0]) + 1
    def __init__(self, a: List[int]) -> None:
        a[0] = a[0] + 1
        self.n = 0

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    k = K(xs)
    return xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
