from typing import Set
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s: Set[int] = {1, 2, 3}
    return len(s)
