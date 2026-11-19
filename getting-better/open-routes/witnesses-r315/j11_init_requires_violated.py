from typing import List

#@ requires len(a) >= 1
#@ ensures \result == a[0]
def first(a: List[int]) -> int:
    return a[0]

class K:
    def __init__(self, a: List[int]) -> None:
        self.n = first(a)

#@ ensures \result == 1
def f() -> int:
    try:
        k = K([])
    except IndexError:
        return 0
    return 1

if __name__ == "__main__":
    assert f() == 1, f()
