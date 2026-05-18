"""Test 0383 — Python Reference 4.2.6: Interaction with dynamic features (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_4_2_6_a(x: int) -> int:
    """Variation A for Interaction with dynamic features."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_4_2_6_a(4) == 5
