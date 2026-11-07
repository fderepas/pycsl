from typing import List
#@ no_exception \all
def f(xs: List[int]) -> List[int]:
    return sorted(xs, key=lambda v: xs[v])

if __name__ == "__main__":
    f([3])
