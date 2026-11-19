from typing import List, Dict

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == a[0]
def inc(a: List[int]) -> int:
    a[0] = a[0] + 1
    return a[0]

#@ ensures \result == False
def f() -> bool:
    xs = [0]
    d: Dict[int, int] = {inc(xs): inc(xs)}
    return 1 in d

if __name__ == "__main__":
    assert f() == False
