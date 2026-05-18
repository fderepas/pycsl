"""Test 0047 — PyCSL Annotation Reference 9.1"""
_ = 0  # anchor
#@ ensures \result == 0
def test_exit_code_zero() -> int:
    """Exit code 0: all goals verified (Valid)."""
    return 0

if __name__ == "__main__":
    assert test_exit_code_zero() == 0
