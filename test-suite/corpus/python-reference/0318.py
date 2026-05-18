"""Test 0318 — Python Reference 3.2.13.1.1: Special read-only attributes (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_13_1_1_b(x: int) -> int:
    """Variation B for Special read-only attributes."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_13_1_1_b(3) == 6
