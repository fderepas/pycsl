"""Test 0381 — interprocedural: callee proves no_exception, caller calls it.

The callee `safe_divide` proves `no_exception ZeroDivisionError`. The
caller does not itself perform any division, so the caller's
`no_exception ZeroDivisionError` is trivially discharged (no triggers
in the caller's body).
"""
_ = 0  # anchor
#@ requires n != 0
#@ ensures \result == 256 / n
#@ assigns \nothing
#@ no_exception ZeroDivisionError
def safe_divide(n: int) -> int:
    return 256 // n

#@ requires n != 0
#@ ensures \result == 256 / n
#@ assigns \nothing
#@ no_exception ZeroDivisionError
def caller(n: int) -> int:
    return safe_divide(n)


if __name__ == "__main__":
    assert caller(8) == 32
