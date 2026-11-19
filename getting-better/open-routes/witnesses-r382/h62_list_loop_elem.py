from typing import List, Dict, Set

#@ no_exception \all
#@ ensures \result == 1
def g(xs: List[List[int]]) -> int:
    for y in xs:
        s = {y}
    return 1

if __name__ == "__main__":
    print(g([[1]]))
