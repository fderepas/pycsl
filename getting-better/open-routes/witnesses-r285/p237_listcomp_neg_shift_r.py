from typing import List

#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(xs: List[int], n: int) -> int:
    ys = [x >> n for x in xs]
    return 1

if __name__ == "__main__":
    f([4], -1)
    print("no exception")
