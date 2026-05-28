"""Test 0393 — no_exception \\all + non-empty raises is rejected by Module 4."""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires True
#@ ensures True
#@ raises ZeroDivisionError when n == 0
#@ no_exception \all
#@ assigns \nothing
def conflicted(n: int) -> int:
    if n == 0:
        raise ZeroDivisionError
    return 256 // n


if __name__ == "__main__":
    pass
