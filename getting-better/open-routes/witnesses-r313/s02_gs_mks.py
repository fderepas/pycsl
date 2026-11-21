from typing import List, Dict, Set

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1
def mkd(a: List[int]) -> Dict[int, int]:
    a[0] = a[0] + 1
    return {0: 1}

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1
def mks(a: List[int]) -> Set[int]:
    a[0] = a[0] + 1
    return {1}

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1
def mkl(a: List[int]) -> List[int]:
    a[0] = a[0] + 1
    return [1]

#@ ensures \result == 0
def gd(p: Dict[int, int]) -> int:
    return 0

#@ ensures \result == 0
def gs(p: Set[int]) -> int:
    return 0

#@ ensures \result == 0
def gl(p: List[int]) -> int:
    return 0

#@ ensures \result == 0
def f() -> int:
    xs = [0]
    v = gs(mks(xs))
    return xs[0]

if __name__ == "__main__":
    assert f() == 0, f()
