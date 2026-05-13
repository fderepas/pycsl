"""Phase 5: label + \at on a scalar variable, Hoare model friendly."""

#@ requires x >= 0
#@ ensures \result == x + 1
#@ assigns \nothing
def next_val(x: int) -> int:
    #@ label L
    r = x + 1
    return r
