from typing import Dict, List

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == 0
def bump(a: List[int]) -> int:
    a[0] = a[0] + 1
    return 0

#@ requires len(xs) == 1 and xs[0] == 0
#@ requires 1 in d
#@ assigns xs[0]
#@ ensures xs[0] == 0
def f(d: Dict[int, int], xs: List[int]) -> int:
    return d.get(1, bump(xs))

if __name__ == "__main__":
    b = [0]
    f({1: 5}, b)
    assert b[0] == 0
