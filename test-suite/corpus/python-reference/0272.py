"""Test 0272 — Python Reference 2.5.5: Bytes literals (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_5_5_b(x: int) -> int:
    """Variation B for Bytes literals."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_5_5_b(3) == 6
