"""Test 0158 — Python Reference 6.10.1: Value comparisons"""
_ = 0  # anchor
#@ ensures \result == 1
def test_value_comparisons() -> int:
    """==, !=, <, >, <=, >=."""
    if 1 < 2 <= 2 < 3:
        return 1
    return 0

if __name__ == "__main__":
    assert test_value_comparisons() == 1
