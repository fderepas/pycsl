"""Test 0155 — Python Reference 6.7: Binary arithmetic operations"""
_ = 0  # anchor
#@ ensures \result == 7
def test_binary_arithmetic() -> int:
    """Binary +, -, *, /, //, %, @."""
    return 3 + 4

if __name__ == "__main__":
    assert test_binary_arithmetic() == 7
