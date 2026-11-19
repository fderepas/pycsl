from typing import List

#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(xs: List[int], n: int) -> int:
    s = sum(1 << x for x in xs)
    return 1

if __name__ == "__main__":
    f([-1], 0)
    print("no exception")
