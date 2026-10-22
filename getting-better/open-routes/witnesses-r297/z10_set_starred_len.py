from typing import List, Dict, Set, Tuple, Optional

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    ys: List[int] = [7, 8]
    s = {*ys}
    return len(s)
if __name__ == "__main__":
    assert f() == 1, f()
