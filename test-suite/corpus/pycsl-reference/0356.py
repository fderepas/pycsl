"""Test 0356 — no_exception parser rejection: no_exception E together with
raises { E -> _ } is a contradiction; Module4 must reject it.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires True
#@ ensures \result >= 0
#@ raises ZeroDivisionError when n == 0
#@ no_exception ZeroDivisionError
#@ assigns \nothing
def conflicted(n: int) -> int:
    if n == 0:
        raise ZeroDivisionError
    return 256 // n


if __name__ == "__main__":
    pass
