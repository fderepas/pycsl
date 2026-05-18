"""Test 0156 — Python Reference 6.8: Shifting operations"""
_ = 0  # anchor
#@ ensures \result == 4
def test_shifting_operations() -> int:
    """<< and >> shift bits."""
    return 1 << 2

if __name__ == "__main__":
    assert test_shifting_operations() == 4
