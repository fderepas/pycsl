from typing import List

#@ requires \length(x) > 0
#@ ensures \length(\result) == \length(x)
#@ ensures \result[0] == x[0]
#@ assigns \nothing
def pick(x: List[int], y: List[int]) -> List[int]:
    if len(x) > 0:
        return x
    return y

#@ ensures \result == 1
def f() -> int:
    a: List[int] = [1]
    c: List[int] = [2]
    b = pick(a, c)
    a[0] = 5
    return b[0]

if __name__ == "__main__":
    assert f() == 1, f()
