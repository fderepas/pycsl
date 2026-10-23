from typing import List, Dict, Set
from dataclasses import dataclass

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

class K:
    def __init__(self, n: int) -> None:
        self.n = n

class L:
    def __init__(self, p: List[int]) -> None:
        self.p = p

@dataclass
class P:
    n: int

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    ys = [1, 2, 3]
    l = L(ys[0:inc(xs)])
    return xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
