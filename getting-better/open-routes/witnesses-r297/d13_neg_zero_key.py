from typing import List, Dict, Set, Tuple, Optional

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {0: 1, -0: 2}
    return d[0]
if __name__ == "__main__":
    assert f() == 1, f()
