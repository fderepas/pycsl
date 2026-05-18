"""Test 0153 — PyCSL Annotation Reference 9.1 (variation B)"""
_ = 0  # anchor
#@ ensures \result == 1
def test_one() -> int:
    """Exit code 0: constant function."""
    return 1

if __name__ == "__main__":
    assert test_one() == 1
