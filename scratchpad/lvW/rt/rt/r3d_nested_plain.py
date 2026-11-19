from typing import Tuple

#@ requires True
#@ ensures x > 0 ==> \result == 1
def outer(x: int) -> int:
    #@ requires True
    #@ ensures y > 0 ==> \result[0] == True
    def inner(y: int) -> Tuple[bool, str]:
        if y > 0:
            return True, ""
        return False, "n"
    t = inner(x)
    if t[0]:
        return 1
    return 0
