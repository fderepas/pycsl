from typing import List

#@ requires \length(x) > 0
#@ ensures \length(\result) == \length(x)
#@ assigns \nothing
def pick(x: List[int], y: List[int]) -> List[int]:
    if len(x) > 0:
        return x
    return y

#@ ensures \result == 1
def f() -> int:
    a: List[int] = [1]
    c: List[int] = [2]
    b: List[int] = pick(a, c)
    b[0] = 5
    return a[0]

if __name__ == "__main__":
    assert f() == 1, f()
