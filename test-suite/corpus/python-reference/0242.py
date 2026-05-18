"""Test 0242 — Python Reference 2.1.10: End marker (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_1_10_b(x: int) -> int:
    """Variation B for End marker."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_1_10_b(3) == 6
