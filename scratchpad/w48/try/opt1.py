from typing import Optional

#@ requires True
#@ ensures \result != None ==> n > 0
#@ assigns \nothing
def g(n: int) -> Optional[int]:
    if n > 0:
        return 5
    return None
