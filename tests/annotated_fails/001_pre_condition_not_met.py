
#@ requires x >= 0
#@ ensures \result == x * 2
#@ assigns \nothing
def multiply_by_two(x: int) -> int:
    return x * 2


#@ ensures \result == x * 2
#@ assigns \nothing
def call_multiply_by_two(x: int) -> int:
    a = multiply_by_two(-2)
    return a
