from typing import List
#@ no_exception \all
def f(xs: List[int]) -> List[int]:
    return sorted(xs, key=lambda v: 10 // v)

if __name__ == "__main__":
    f([0, 1])
