"""Test 0321 — Python Reference 3.2.13.2.1: Special read-only attributes (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_2_13_2_1_a(x: int) -> int:
    """Variation A for Special read-only attributes."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_2_13_2_1_a(4) == 5
