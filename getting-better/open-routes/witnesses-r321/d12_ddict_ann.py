from collections import defaultdict
from typing import Dict
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    d = {1: 5}
    a: Dict[int, int] = defaultdict(int, d)
    d = {1: 6}
    b: Dict[int, int] = defaultdict(int, d)
    if a[1] != b[1]:
        return 1
    return 0

if __name__ == "__main__":
    assert f() == 0, f()
