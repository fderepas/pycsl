from typing import List
#@ no_exception \all
def f(xs: List[float]) -> int:
    y = float(sum(xs))
    return 0
if __name__ == "__main__":
    print(f([1.5]))
