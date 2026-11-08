from typing import List

#@ requires \length(x) > 0
#@ ensures \length(\result) == \length(x)
#@ assigns \nothing
def first_nonempty(x: List[int]) -> List[int]:
    for i in range(3):
        if i == 1:
            return x
    return x

#@ ensures \result == 1
def f() -> int:
    a: List[int] = [1]
    b = first_nonempty(a)
    b[0] = 5
    return a[0]

if __name__ == "__main__":
    assert f() == 1, f()
