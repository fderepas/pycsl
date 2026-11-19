from typing import List, Dict, Set, Tuple, Optional

#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    ys: List[int] = [7, 8]
    t = (*ys, 5)
    return t[1]
if __name__ == "__main__":
    assert f() == 5, f()
