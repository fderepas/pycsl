"""Test 0285 — Python Reference 2.6.3: Imaginary literals (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_6_3_a(x: int) -> int:
    """Variation A for Imaginary literals."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_6_3_a(4) == 5
