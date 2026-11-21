from typing import List

#@ requires len(e) == 1
#@ ensures \result == 0
#@ assigns \nothing
def g(e: List[int]) -> int:
    t = 0
    [*h, t] = e
    return t

if __name__ == "__main__":
    assert g([5]) == 5
