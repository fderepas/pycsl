from typing import Dict, List

#@ no_exception \all
#@ ensures \result == 1
def f(a: List[int]) -> int:
    d: Dict[int, int] = {1: 1}
    return d.get(1, a[5])

if __name__ == "__main__":
    assert f([]) == 1
