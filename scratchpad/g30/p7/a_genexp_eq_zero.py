from typing import List


#@ ensures \result == 1
def probe() -> int:
    g = (x for x in [1, 2, 3])
    if g == 0:
        return 1
    return 2
