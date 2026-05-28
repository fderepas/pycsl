"""Test 0360 — ZeroDivisionError annotated, no precondition: fails.

The function declares `no_exception ZeroDivisionError` but does not
strengthen the precondition. Module 6 emits `assert { no_div_zero n }`
and Why3 cannot discharge it (n is unconstrained), so verification
fails as expected.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires True
#@ ensures True
#@ assigns \nothing
#@ no_exception ZeroDivisionError
def unsafe_divide(n: int) -> int:
    return 256 // n


if __name__ == "__main__":
    pass
