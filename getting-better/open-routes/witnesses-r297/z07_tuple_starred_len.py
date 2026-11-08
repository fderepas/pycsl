from typing import List, Dict, Set, Tuple, Optional

#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    ys: List[int] = [7, 8]
    t = (*ys, 5)
    return len(t)
if __name__ == "__main__":
    assert f() == 2, f()
