"""Test 0294 — Python Reference 3.2.8.2: Instance methods (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_8_2_b(x: int) -> int:
    """Variation B for Instance methods."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_8_2_b(3) == 6
