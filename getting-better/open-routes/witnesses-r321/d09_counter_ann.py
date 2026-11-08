from collections import Counter
from typing import Dict
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    xs = [1, 1]
    c1: Dict[int, int] = Counter(xs)
    xs = [2]
    c2: Dict[int, int] = Counter(xs)
    if c1[1] != c2[1]:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 0, f()
