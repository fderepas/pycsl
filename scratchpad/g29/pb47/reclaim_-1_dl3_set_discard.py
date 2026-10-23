from typing import Set
_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    s: Set[int] = {1, 2}
    s.discard(1)
    if 1 in s:
        return 1
    return 0
