from typing import List
_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    n: int = 0
    for x in [1, 2]:
        n = n + x
    else:
        n = n + 100
    return n
