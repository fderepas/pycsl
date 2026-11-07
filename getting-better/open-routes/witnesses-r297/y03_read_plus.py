from typing import List, Dict, Set, Tuple, Optional

#@ ensures \result == 1
#@ assigns \nothing
def f(k: int) -> int:
    d: Dict[int, int] = {0: 1, k: 2}
    r = d[0]
    return r + 0
if __name__ == "__main__":
    assert f(0) == 1, f(0)
