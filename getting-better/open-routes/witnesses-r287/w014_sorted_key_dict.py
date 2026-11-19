from typing import List, Dict
#@ no_exception \all
def f(xs: List[int], d: Dict[int, int]) -> List[int]:
    return sorted(xs, key=lambda v: d[v])

if __name__ == "__main__":
    f([3], {})
