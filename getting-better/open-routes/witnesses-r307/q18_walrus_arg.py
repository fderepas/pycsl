from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == a - b
def sub(a: int, b: int) -> int:
    return a - b

#@ ensures \result == 0
def f() -> int:
    x = 1
    return sub(x, (x := 5))

if __name__ == "__main__":
    assert f() == 0
