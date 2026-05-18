"""Test 0486 — Python Reference 8.4.4: :keyword:`!finally` clause (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_8_4_4_b(x: int) -> int:
    """Variation B for :keyword:`!finally` clause."""
    return x + x

if __name__ == "__main__":
    assert test_ref_8_4_4_b(3) == 6
