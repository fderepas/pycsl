from typing import List
#@ ensures \result == True
#@ assigns \nothing
def g(xs: List[int]) -> bool:
    N = len(xs)
    n = 0
    return N == n

if __name__ == "__main__":
    assert g([1, 2]) == True
