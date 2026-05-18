"""Test 0154 — Python Reference 6.6: Unary arithmetic and bitwise operations"""
_ = 0  # anchor
#@ ensures \result == 5
def test_unary_arithmetic_bitwise() -> int:
    """Unary +, -, ~."""
    x = -(-5)
    return x

if __name__ == "__main__":
    assert test_unary_arithmetic_bitwise() == 5
