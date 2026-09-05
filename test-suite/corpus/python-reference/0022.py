"""Test 0022 — Python Reference 2.1.5: Explicit line joining"""
_ = 0  # anchor
#@ ensures \result == 10
#@ assigns \nothing
def test_ignored_end_of_line() -> int:
    """Ref 2.1.5: a backslash at the end of a physical line joins it to the next, so the
    expression below is ONE logical line and evaluates to 10. Previously the whole body
    was `return 0` (relaunch #46, `bin/check-vacuous-drivers.py`)."""
    total = 1 + \
        2 + \
        3 + \
        4
    return total

if __name__ == "__main__":
    assert test_ignored_end_of_line() == 10
