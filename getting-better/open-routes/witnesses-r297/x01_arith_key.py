from typing import List, Dict, Set, Tuple, Optional

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {1: 1, 2 - 1: 2}
    return d[1]
if __name__ == "__main__":
    assert f() == 1, f()
