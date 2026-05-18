"""Test 0286 — Python Reference 2.6.3: Imaginary literals (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_6_3_b(x: int) -> int:
    """Variation B for Imaginary literals."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_6_3_b(3) == 6
