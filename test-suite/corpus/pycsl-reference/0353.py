"""Test 0353 — no_exception parser: single exception name parses."""
_ = 0  # anchor
#@ requires n != 0
#@ ensures \result == 256 / n
#@ assigns \nothing
#@ no_exception ZeroDivisionError
def divide_256(n: int) -> int:
    return 256 // n


if __name__ == "__main__":
    assert divide_256(4) == 64
