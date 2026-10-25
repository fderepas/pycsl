from typing import Set

#@ no_exception \all
#@ ensures \result == 1
def g(d: Set[int]) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(set()))
