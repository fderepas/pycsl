"""Test 0332 — Python Reference 3.2.13.5: Static method objects (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_13_5_b(x: int) -> int:
    """Variation B for Static method objects."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_13_5_b(3) == 6
