"""Test 0484 — Python Reference 8.4.3: :keyword:`!else` clause (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_8_4_3_b(x: int) -> int:
    """Variation B for :keyword:`!else` clause."""
    return x + x

if __name__ == "__main__":
    assert test_ref_8_4_3_b(3) == 6
