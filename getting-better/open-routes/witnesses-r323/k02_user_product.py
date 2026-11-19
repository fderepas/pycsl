from typing import List


#@ assigns \nothing
def product(a: List[int], b: List[int]) -> List[int]:
    return [0]

#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return len(list(product([1, 2], [3, 4])))

if __name__ == "__main__":
    assert f() == 4, f()
