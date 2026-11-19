from typing import Tuple

#@ requires True
#@ ensures True
def outer(x: int) -> int:
    def inner(y: int) -> Tuple[bool, str]:
        if y > 0:
            return True, ""
        return False, "n"
    ok, msg = inner(x)
    if ok:
        return 1
    return 0
