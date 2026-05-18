"""Test 0277 — Python Reference 2.5.8: t-strings (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_5_8_a(x: int) -> int:
    """Variation A for t-strings."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_5_8_a(4) == 5
