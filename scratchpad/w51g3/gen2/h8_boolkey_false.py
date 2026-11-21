from typing import Dict

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {1: 5, True: 6}
    if len(d) == 2:
        return 1
    return 0
