"""Test 0356 — Python Reference 3.3.6: Emulating callable objects (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_3_6_b(x: int) -> int:
    """Variation B for Emulating callable objects."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_3_6_b(3) == 6
