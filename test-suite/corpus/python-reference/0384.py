"""Test 0384 — Python Reference 4.2.6: Interaction with dynamic features (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_4_2_6_b(x: int) -> int:
    """Variation B for Interaction with dynamic features."""
    return x + x

if __name__ == "__main__":
    assert test_ref_4_2_6_b(3) == 6
