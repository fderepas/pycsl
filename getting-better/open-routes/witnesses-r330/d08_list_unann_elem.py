from typing import List
#@ ensures \result == True
#@ assigns \nothing
def g(xs: List) -> bool:
    return xs[0] % 1 == 0

if __name__ == "__main__":
    assert g([0.5]) == True
