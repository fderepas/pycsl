from typing import Tuple

#@ requires True
#@ ensures \result[0] == True ==> \result[1] == ""
def f(x: int) -> Tuple[bool, str]:
    k = 0
    try:
        if x > 0:
            return True, "x"
    finally:
        k = k + 1
    return False, "neg"
