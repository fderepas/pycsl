"""Test 0296 — Python Reference 3.2.8.3: Generator functions (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_8_3_b(x: int) -> int:
    """Variation B for Generator functions."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_8_3_b(3) == 6
