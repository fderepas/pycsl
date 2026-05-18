"""Test 0110 — Python Reference 4.4.1: General Computing Model"""
_ = 0  # anchor
#@ ensures \result == 0
def test_exception_handling() -> int:
    """try/except catches exceptions."""
    try:
        x = 1 / 0
    except ZeroDivisionError:
        return 0
    return 1

if __name__ == "__main__":
    assert test_exception_handling() == 0
