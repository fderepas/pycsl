from typing import List, Dict, Tuple

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result[1] == 1 and \result[0] == 1
def f() -> Tuple[int, int]:
    c = [0]
    return c[0], inc(c)

if __name__ == "__main__":
    t = f()
    assert t[1] == 1 and t[0] == 1
