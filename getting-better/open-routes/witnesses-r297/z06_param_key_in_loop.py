from typing import List, Dict, Set, Tuple, Optional

#@ requires n >= 1
#@ ensures \result == 1
#@ assigns \nothing
def f(n: int) -> int:
    i = n - 1
    d: Dict[int, int] = {0: 1, i: 2}
    return d[0]
if __name__ == "__main__":
    assert f(1) == 1, f(1)
