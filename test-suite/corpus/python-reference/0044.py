"""Test 0044 — Python Reference 3.2.4.3: numbers.Complex (complex)"""
_ = 0  # anchor
#@ ensures \result == 0
def test_numbers_complex() -> int:
    """Complex numbers have real and imag parts."""
    c = 3 + 4j
    assert c.real == 3.0
    assert c.imag == 4.0
    return 0

if __name__ == "__main__":
    assert test_numbers_complex() == 0
