from typing import Tuple

#@ requires True
#@ ensures \result[0] == True ==> \result[1] == ""
def f(x: int) -> Tuple[bool, str]:
    if x > 0:
        return True, ""
    return False, "neg"

#@ requires True
#@ ensures \result[0] == x and \result[1] == "a"
def g(x: int) -> Tuple[int, str]:
    if x > 0:
        return x, "a"
    return x, "a"

#@ requires True
#@ ensures \result[1] == "b"
def h(x: int) -> Tuple[bool, str]:
    if x > 0:
        return False, "b"
    return True, "b"
