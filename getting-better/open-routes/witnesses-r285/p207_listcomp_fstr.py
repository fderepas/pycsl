from typing import List

#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(xs: List[int]) -> int:
    ss = [f"{x}" for x in xs]
    return 1

if __name__ == "__main__":
    f([10**5000])
    print("no exception")
