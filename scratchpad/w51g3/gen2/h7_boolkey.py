from typing import Dict

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {True: 5}
    if d[1] == 5:
        return 1
    return 0
