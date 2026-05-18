"""Test 0043 — Python Reference 3.2.4.2: numbers.Real (float)"""
_ = 0  # anchor
#@ ensures \result == 3
def test_numbers_real() -> int:
    """Floats (numbers.Real) use double-precision."""
    x = 3.14
    return int(x)

if __name__ == "__main__":
    assert test_numbers_real() == 3
