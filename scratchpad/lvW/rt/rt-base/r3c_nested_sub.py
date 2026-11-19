from typing import Tuple

#@ requires True
#@ ensures \result == 1
def outer(x: int) -> int:
    #@ requires True
    #@ ensures \result[0] == True ==> \result[1] == ""
    def inner(y: int) -> Tuple[bool, str]:
        if y > 0:
            return True, ""
        return False, "n"
    t = inner(x)
    if t[0] and t[1] != "":
        return 0
    return 1
