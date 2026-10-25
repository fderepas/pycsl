from typing import List, Dict, Set

#@ no_exception \all
#@ ensures \result == 1
def g(xs: List[int]) -> int:
    s = {xs}
    return 1

if __name__ == "__main__":
    print(g([1]))
