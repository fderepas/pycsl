"""Test 0022 — Python Reference 2.5.4.1: Ignored end of line"""
_ = 0  # anchor
#@ ensures \result == 0
def test_ignored_end_of_line() -> int:
    """Ref 2.5.4.1: Ignored end of line."""
    return 0

if __name__ == "__main__":
    assert test_ignored_end_of_line() == 0
