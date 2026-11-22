#@ requires x > 0 and x < 0
#@ ensures \result == 99
def function(x: int) -> int:
    return 1

#@ requires x > 0 and x < 0
#@ ensures \result == 99
def ghost(x: int) -> int:
    return 1

#@ requires x > 0 and x < 0
#@ ensures \result == 99
def rec(x: int) -> int:
    return 1
