"""Test 0361 — ZeroDivisionError annotated, strengthened precondition.

Precondition `n != 0` discharges the inline `assert { no_div_zero n }`,
so the function proves.
"""
_ = 0  # anchor
#@ requires n != 0
#@ ensures \result == 256 // n
#@ assigns \nothing
#@ no_exception ZeroDivisionError
def safe_divide(n: int) -> int:
    return 256 // n


if __name__ == "__main__":
    assert safe_divide(8) == 32
