"""Test 0157 — Python Reference 6.9: Binary bitwise operations"""
_ = 0  # anchor
#@ ensures \result == 2
def test_binary_bitwise() -> int:
    """&, |, ^ bitwise operations."""
    return 3 & 2

if __name__ == "__main__":
    assert test_binary_bitwise() == 2
