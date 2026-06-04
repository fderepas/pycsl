"""Test 0457 — PyCSL statement-level proof obligations: #@ assert / #@ check."""
_ = 0  # anchor
#@ requires x > 0
#@ ensures \result == x + 1
def stepper(x: int) -> int:
    #@ assert x > 0
    #@ check x >= 1
    y = x + 1
    return y
