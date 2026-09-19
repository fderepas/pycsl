from typing import List, Optional


#@ ensures \result == 1
def probe() -> int:
    xs: List[Optional[int]] = []
    xs.append(None)
    v = xs[0]
    if v == 0:
        return 1
    return 2
