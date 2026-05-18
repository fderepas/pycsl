"""Test 0042 — Python Reference 3.2.4.1: numbers.Integral"""
_ = 0  # anchor
#@ requires x >= 0
#@ ensures \result == x + 1
def test_numbers_integral(x: int) -> int:
    """Integers (numbers.Integral) have unlimited precision."""
    return x + 1

if __name__ == "__main__":
    assert test_numbers_integral(0) == 1
    assert test_numbers_integral(10**100) == 10**100 + 1
