"""Test 0131 — Python Reference 6.1: Arithmetic conversions"""
_ = 0  # anchor
#@ ensures \result == 3
def test_arithmetic_conversions() -> int:
    """Numeric conversions: int -> float for mixed ops."""
    x = int(3.7)
    return x

if __name__ == "__main__":
    assert test_arithmetic_conversions() == 3
