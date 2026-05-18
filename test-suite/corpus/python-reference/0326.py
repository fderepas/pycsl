"""Test 0326 — Python Reference 3.2.13.2.3: Frame object methods (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_13_2_3_b(x: int) -> int:
    """Variation B for Frame object methods."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_13_2_3_b(3) == 6
