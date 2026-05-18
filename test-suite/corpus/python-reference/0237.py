"""Test 0237 — Python Reference 2.1.8: Indentation (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_1_8_a(x: int) -> int:
    """Variation A for Indentation."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_1_8_a(4) == 5
